#! /bin/bash

VIDEO_NAME="rtcWebcam"
NUM_DEVICES=1
EXCLUSIVE_CAPS="1"

if [ $(lsmod | grep v4l2loopback | wc -l) -eq 0 ]; then
    echo "Loading v4l2loopback module...\n"
    sudo modprobe v4l2loopback devices=$NUM_DEVICES exclusive_caps=$EXCLUSIVE_CAPS card_label="$VIDEO_NAME"
else 
    echo "v4l2loopback module already loaded."
    echo "To avoid errors, it is recommended to reload v4l2loopback before running this script."
    read -r -p "Do you want to reload it? [y/N] " RELOAD_MODULE
    if [ "$RELOAD_MODULE" = "y" ]; then
        sudo rmmod v4l2loopback
        if [ $? -eq 0 ]; then
            echo "v4l2loopback module unloaded successfully."
        else
            echo "v4l2loopback module reload failed.\n"
            exit 1
        fi
        sudo modprobe v4l2loopback devices=$NUM_DEVICES exclusive_caps=$EXCLUSIVE_CAPS card_label="$VIDEO_NAME"
    fi
fi
if [ $? -eq 0 ]; then
    echo "v4l2loopback module loaded successfully.\n"
else
    echo "v4l2loopback module loading failed.\n"
    exit 1
fi

sink_module=$(pactl load-module module-null-sink sink_name=virtualMic sink_properties=device.description=virtualMic)
source_module=$(pactl load-module module-remap-source master=virtualMic.monitor source_name=virtualMicDiscord source_properties=device.description=virtualMicDiscord)
echo "pulseaudio modules loaded successfully."

python3 main.py $VIDEO_NAME

pactl unload-module $sink_module
pactl unload-module $source_module
echo "pulseaudio modules unloaded successfully."

sudo rmmod v4l2loopback
if [ $? -eq 0 ]; then
    echo "v4l2loopback module unloaded successfully."
else
    echo "v4l2loopback module reload failed.\n"
    exit 1
fi

