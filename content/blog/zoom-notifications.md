---
title: "Hacks for Zoom chat notifications"
date: 2021-12-02 17:25:08 +0800
---

Sometimes all you need is for your computer to tell you when something on the screen changes.
Maybe you're invigilating an exam over Zoom and your eyes are drying out from staring at the chat window, which does not (and probably will never) have any notification settings.

# Rectangles

The first piece is how to capture a small region of the screen.
Interestingly, this is [built into](https://superuser.com/questions/875342/how-can-i-repeatedly-take-a-screenshot-of-a-specific-area-in-os-x) the `screencapture` command, which takes the coordinates and dimensions of a rectangular area to capture.

We could fudge around until we get the right coordinates, but there's a better way in AppKit.
This tiny Objective-C program (from [here](https://macscripter.net/viewtopic.php?pid=130549#p130549)) prints the current coordinates of the mouse (with the origin at the top-left).


```objc
#import <AppKit/AppKit.h>

int main (int argc, const char * argv[]) {
   NSAutoreleasePool * pool = [[NSAutoreleasePool alloc] init];

   NSRect e = [[NSScreen mainScreen] frame];
   int H = e.size.height;

   NSPoint mouseLoc = [NSEvent mouseLocation];
   // origin is now at the top left
   NSString* locString = [NSString stringWithFormat:@"%d\n%d", (int) mouseLoc.x, H - (int) mouseLoc.y];
   printf("%s\n", [locString UTF8String]);

   [pool drain];
   return 0;
}
```

```sh
gcc -o MouseLocation MouseLocation.m -framework AppKit
```

# Notifications

We also need a way to show a notification.
A simple way is to use [iTerm-specific escape codes](https://iterm2.com/documentation-escape-codes.html); we simply surround the text we want to show with them.

```sh
notify() {
  echo $'\e]9;'$1$'\007'
}
```

We could also use [AppleScript](https://developer.apple.com/library/archive/documentation/LanguagesUtilities/Conceptual/MacAutomationScriptingGuide/DisplayNotifications.html), which allows us to provide a title.

```sh
notify() {
  osascript -e "display notification \"$2\" with title \"$1\""
}
```

# Glue

Everything is glued together with this terrible script:

```sh
#!/usr/bin/env bash

tlx=$1
tly=$2
brx=$3
bry=$4

capture() {
  screencapture -x -R $tlx,$tly,$(($brx-$tlx)),$(($bry-$tly)) /tmp/screen.png
}

set -x

capture
res="$(md5 /tmp/screen.png)"
prev="$res"

while true; do
  sleep 5
  capture
  res="$(md5 /tmp/screen.png)"
  if [ "$res" != "$prev" ]; then
    notify "Something changed!"
    exit 0
  fi
  prev="$res"
done
```

The arguments are the coordinates we get from running `./MouseLocation` twice, with the mouse cursor at the top-left and bottom-right of the rectangle we want to watch.

One thing that appears silly to do (and is very much in the spirit of this post) is the use of MD5 for comparing images.
We want to be notified if _anything_ changes, and for this use case a more sophisticated image diff like ImageMagick's `compare` wouldn't add much.
`screencapture` is thankfully deterministic as well, so this all works.
For something more resilient to small variations, you might want to use one of the [metrics](https://imagemagick.org/script/compare.php) offered by ImageMagick.

# Verdict

This is really janky but works surprisingly well.
