#!/bin/bash
tim=1;
iterations=3;
for ((i=1;i<=iterations;i++)); do
  echo "iteration $i"
  xdotool mousemove --sync 231 190 click 1 &&
  sleep "$tim" &&
  xdotool mousemove --sync 281 233 click 1 &&
  sleep "$tim" &&
  xdotool mousemove --sync 765 241 &&
  sleep "$tim" &&
  echo "step 4" &&
  xdotool mousemove --sync 828 538 click 1 &&
  sleep 120
done
