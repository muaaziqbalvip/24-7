#!/bin/bash
# ============================================
# 24/7 LIVE STREAM ENGINE v2.0
# Firebase Realtime Control System
# ============================================

FIREBASE_URL="https://ramadan-2385b-default-rtdb.firebaseio.com"
LOG_FILE="/tmp/stream.log"
LOOP_COUNT=0
MAX_LOOPS=50

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Push status to Firebase
push_status() {
  local status="$1"
  local msg="$2"
  curl -s -X PUT "$FIREBASE_URL/stream_status.json" \
    -H "Content-Type: application/json" \
    -d "{\"status\":\"$status\",\"message\":\"$msg\",\"timestamp\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",\"loop\":$LOOP_COUNT}" > /dev/null
}

# Fetch current config from Firebase
get_config() {
  curl -s "$FIREBASE_URL/stream_config.json" 2>/dev/null || echo "{}"
}

# Extract yt-dlp supported URL to direct stream
resolve_url() {
  local url="$1"
  # If it's already a direct stream link
  if [[ "$url" == *.m3u8 ]] || [[ "$url" == *.mp4 ]] || [[ "$url" == *.mkv ]] || [[ "$url" == *.mp3 ]] || [[ "$url" == *.m3u ]]; then
    echo "$url"
    return
  fi
  # Try yt-dlp for YouTube/other platforms
  if command -v yt-dlp &>/dev/null; then
    yt-dlp -g --no-warnings "$url" 2>/dev/null | head -1
  else
    echo "$url"
  fi
}

# Install yt-dlp if needed
setup_tools() {
  if ! command -v yt-dlp &>/dev/null; then
    log "Installing yt-dlp..."
    pip install yt-dlp -q 2>/dev/null || pip3 install yt-dlp -q 2>/dev/null
  fi
}

# Build FFmpeg filter complex for overlays
build_ffmpeg_cmd() {
  local input_url="$1"
  local config="$2"

  # Parse config
  local show_ticker=$(echo "$config" | jq -r '.show_ticker // "true"')
  local ticker_text=$(echo "$config" | jq -r '.ticker_text // "LIVE BROADCAST"')
  local show_logo=$(echo "$config" | jq -r '.show_logo // "false"')
  local logo_pos=$(echo "$config" | jq -r '.logo_position // "top-left"')
  local show_clock=$(echo "$config" | jq -r '.show_clock // "true"')
  local clock_tz=$(echo "$config" | jq -r '.clock_timezone // "UTC"')
  local pitch=$(echo "$config" | jq -r '.audio_pitch // "1.0"')
  local volume=$(echo "$config" | jq -r '.audio_volume // "1.0"')
  local output_url=$(echo "$config" | jq -r '.output_url // ""')
  local resolution=$(echo "$config" | jq -r '.resolution // "1280x720"')
  local bitrate=$(echo "$config" | jq -r '.bitrate // "2500k"')

  local width=$(echo "$resolution" | cut -d'x' -f1)
  local height=$(echo "$resolution" | cut -d'x' -f2)

  # Build filter complex
  local vf_filters=""
  local filter_complex=""

  # Scale base
  filter_complex="[0:v]scale=${width}:${height}:force_original_aspect_ratio=decrease,pad=${width}:${height}:(ow-iw)/2:(oh-ih)/2,setsar=1[base];"

  # Ticker bar (scrolling bottom)
  if [ "$show_ticker" = "true" ]; then
    local escaped_text=$(echo "$ticker_text" | sed "s/'/\\\\\\\\'/g" | sed "s/:/\\\\:/g")
    filter_complex="${filter_complex}[base]drawtext=text='${escaped_text}':fontsize=28:fontcolor=white:box=1:boxcolor=black@0.7:boxborderw=8:x=w-mod(t*120\\,w+tw):y=h-60[tickered];"
    local last="tickered"
  else
    local last="base"
  fi

  # Clock overlay
  if [ "$show_clock" = "true" ]; then
    filter_complex="${filter_complex}[${last}]drawtext=text='%{localtime\\:%H\\:%M\\:%S}':fontsize=32:fontcolor=white:box=1:boxcolor=black@0.8:boxborderw=6:x=w-200:y=10[clocked];"
    local last="clocked"
  fi

  # Date overlay
  filter_complex="${filter_complex}[${last}]drawtext=text='%{localtime\\:%d %b %Y}':fontsize=22:fontcolor=yellow:box=1:boxcolor=black@0.6:boxborderw=4:x=w-200:y=50[dated];"
  local last="dated"

  # LIVE badge
  filter_complex="${filter_complex}[${last}]drawtext=text='🔴 LIVE':fontsize=30:fontcolor=red:box=1:boxcolor=white@0.9:boxborderw=8:x=10:y=10[livebadge];"
  local last="livebadge"

  # Audio filters
  local audio_filter="volume=${volume},asetrate=44100*${pitch},aresample=44100"

  # Output to HLS
  local HLS_DIR="/tmp/hls"
  mkdir -p "$HLS_DIR"

  local ffmpeg_cmd="ffmpeg -re -i \"$input_url\" \
    -filter_complex \"${filter_complex}\" \
    -map \"[${last}]\" \
    -af \"${audio_filter}\" \
    -c:v libx264 -preset veryfast -b:v ${bitrate} -maxrate ${bitrate} -bufsize 4000k \
    -c:a aac -b:a 128k -ar 44100 \
    -f hls \
    -hls_time 4 \
    -hls_list_size 10 \
    -hls_flags delete_segments+append_list \
    -hls_segment_filename \"${HLS_DIR}/seg%05d.ts\" \
    \"${HLS_DIR}/stream.m3u8\" \
    -y 2>&1"

  echo "$ffmpeg_cmd"
}

# Main stream loop
main() {
  log "🚀 Stream Engine Starting..."
  setup_tools
  push_status "starting" "Stream engine initializing"

  local HLS_DIR="/tmp/hls"
  mkdir -p "$HLS_DIR"

  while [ $LOOP_COUNT -lt $MAX_LOOPS ]; do
    LOOP_COUNT=$((LOOP_COUNT + 1))
    log "📡 Loop #$LOOP_COUNT starting..."
    push_status "live" "Stream running - Loop $LOOP_COUNT"

    # Fetch fresh config
    local config=$(get_config)
    log "Config fetched: $config"

    # Check if stream is enabled
    local enabled=$(echo "$config" | jq -r '.enabled // "true"')
    if [ "$enabled" = "false" ]; then
      log "⏸️ Stream paused by control room"
      push_status "paused" "Paused from control room"
      sleep 30
      continue
    fi

    # Get source URL
    local source_url=$(echo "$config" | jq -r '.source_url // ""')

    if [ -z "$source_url" ] || [ "$source_url" = "null" ]; then
      log "⚠️ No source URL. Using default test stream..."
      source_url="https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8"
    fi

    # Resolve URL (YouTube/etc)
    log "🔗 Resolving: $source_url"
    local resolved_url=$(resolve_url "$source_url")
    if [ -z "$resolved_url" ]; then
      resolved_url="$source_url"
    fi
    log "✅ Resolved to: $resolved_url"

    # Get schedule - check if it's show time
    local schedule_enabled=$(echo "$config" | jq -r '.schedule_enabled // "false"')
    if [ "$schedule_enabled" = "true" ]; then
      local schedule_source=$(echo "$config" | jq -r '.schedule_source // ""')
      if [ -n "$schedule_source" ] && [ "$schedule_source" != "null" ]; then
        log "📅 Schedule mode - using scheduled source"
        resolved_url=$(resolve_url "$schedule_source")
      fi
    fi

    # Build and run FFmpeg
    local pitch=$(echo "$config" | jq -r '.audio_pitch // "1.0"')
    local volume=$(echo "$config" | jq -r '.audio_volume // "1.0"')
    local resolution=$(echo "$config" | jq -r '.resolution // "1280x720"')
    local bitrate=$(echo "$config" | jq -r '.bitrate // "2500k"')
    local show_ticker=$(echo "$config" | jq -r '.show_ticker // "true"')
    local ticker_text=$(echo "$config" | jq -r '.ticker_text // "LIVE BROADCAST - 24/7"')
    local width=$(echo "$resolution" | cut -d'x' -f1)
    local height=$(echo "$resolution" | cut -d'x' -f2)

    # Escape ticker text
    local safe_ticker=$(echo "$ticker_text" | sed "s/'//g" | sed 's/://g')

    # Build FFmpeg filter
    FILTER="[0:v]scale=${width}:${height}:force_original_aspect_ratio=decrease,pad=${width}:${height}:(ow-iw)/2:(oh-ih)/2,setsar=1"

    # Add ticker
    if [ "$show_ticker" = "true" ]; then
      FILTER="${FILTER},drawtext=text='${safe_ticker}   •   ${safe_ticker}   •   ':fontsize=28:fontcolor=white:box=1:boxcolor=0x111111@0.85:boxborderw=12:x=w-mod(t*100\\,w+tw*2):y=h-55"
    fi

    # Add clock
    FILTER="${FILTER},drawtext=text='%{localtime\\:%H\\:%M\\:%S}':fontsize=30:fontcolor=white:box=1:boxcolor=black@0.75:boxborderw=5:x=w-190:y=12"

    # Add date
    FILTER="${FILTER},drawtext=text='%{localtime\\:%d %b %Y}':fontsize=20:fontcolor=FFD700:box=1:boxcolor=black@0.6:boxborderw=4:x=w-190:y=48"

    # Add LIVE badge
    FILTER="${FILTER},drawtext=text='  LIVE  ':fontsize=28:fontcolor=white:box=1:boxcolor=CC0000@0.95:boxborderw=8:x=12:y=12"

    # Audio
    local audio_filter="volume=${volume}"
    if [ "$pitch" != "1.0" ] && [ "$pitch" != "null" ]; then
      audio_filter="${audio_filter},asetrate=44100*${pitch},aresample=44100"
    fi

    log "🎬 Starting FFmpeg stream..."

    timeout 1200 ffmpeg \
      -re \
      -i "$resolved_url" \
      -vf "$FILTER" \
      -af "$audio_filter" \
      -c:v libx264 \
      -preset veryfast \
      -tune zerolatency \
      -b:v "$bitrate" \
      -maxrate "$bitrate" \
      -bufsize 4000k \
      -g 48 \
      -keyint_min 48 \
      -sc_threshold 0 \
      -c:a aac \
      -b:a 128k \
      -ar 44100 \
      -f hls \
      -hls_time 4 \
      -hls_list_size 12 \
      -hls_flags delete_segments+append_list+independent_segments \
      -hls_segment_filename "${HLS_DIR}/seg%05d.ts" \
      -method PUT \
      "${HLS_DIR}/stream.m3u8" \
      -y 2>&1 | tee -a "$LOG_FILE"

    EXIT_CODE=$?
    log "⚠️ FFmpeg exited with code $EXIT_CODE. Restarting in 5s..."
    push_status "restarting" "Auto-restart loop $LOOP_COUNT"
    sleep 5
  done

  push_status "stopped" "Max loops reached - workflow ended"
  log "🔁 Max loops reached. GitHub will restart via schedule."
}

main
