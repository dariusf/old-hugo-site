---
title: "Godot + C# + VSCode (macOS)"
date: 2022-07-15 20:31:50 +0800
---

Install system dependencies:

```fish
brew install --cask mono-mdk dotnet-sdk godot-mono
brew install mono
```

```
$ which dotnet msbuild mono
/usr/local/bin/dotnet
/Library/Frameworks/Mono.framework/Versions/Current/Commands/msbuild
/Library/Frameworks/Mono.framework/Versions/Current/Commands/mono
```

Start Godot and create a project (e.g. `$HOME/godot/hello`).

Add a C# script to a node. This should generate `hello.sln` and `hello.csproj` files.

Set `Editor > Editor Settings > Mono > Editor`, so VSCode will be started when double-clicking script files.

Over to VSCode. Install the following extensions:

- [C#](https://marketplace.visualstudio.com/items?itemName=ms-dotnettools.csharp)
- [C# Tools for Godot](https://marketplace.visualstudio.com/items?itemName=neikeq.godot-csharp-vscode)
- [godot-tools](https://marketplace.visualstudio.com/items?itemName=geequlim.godot-tools)
- [Mono Debug](https://marketplace.visualstudio.com/items?itemName=ms-vscode.mono-debug)

Open the project:

```fish
code $HOME/godot/hello
```

Uncheck `OmniSharp: Use Modern Net` or add this to your settings.

```json
"omnisharp.useModernNet": false
```

Follow the prompts to restart OmniSharp.

At this point, IntelliSense should work for standard types and namespaces, e.g. `List` and `System.Collections.Generic`.
If it doesn't, open the Output view and look at the C# and OmniSharp Log sections, and try to fix the errors there.

Once basic IntelliSense is working, start Godot in a separate terminal.[^1]

```fish
/Applications/Godot_mono.app/Contents/MacOS/Godot --path "$HOME/godot/hello" -e
```

Click `Build` in the top-right corner.

Switch back to VSCode, `Restart OmniSharp`, and IntelliSense should work for Godot APIs like `GD.Print`.[^2]


Debugging seems to just work. Select `View: Show Run and Debug` and click `Play in Editor` on the left.

Other resources:

- [Visual Studio Code and C# code completion and debugger for Godot](https://gist.github.com/paulloz/30ae499c1fc580a2f3ab9ecebe80d9ba) (nice concise guide with screenshots, but some parts are outdated or have missing details)
- [Official guide](https://docs.godotengine.org/en/stable/tutorials/scripting/c_sharp/c_sharp_basics.html)

[^1]: Godot invokes `msbuild`, so this is just to ensure it is started in the appropriate environment.
Alternatively, select `Godot Tools: Open workspace with Godot editor` from the command palette after configuring the path to the editor in the workspace `settings.json`, and this will be done for you in a terminal in VSCode.

    ```json
    "godot_tools.editor_path": "/Applications/Godot_mono.app/Contents/MacOS/Godot"
    ```
[^2]: In the status bar, you should see a flame icon indicating "OmniSharp server is running", and a "Connected" section indicating the GDScript language server (provided by Godot itself) is running.
