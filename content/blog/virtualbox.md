---
title: "VirtualBox for Docker users"
date: 2021-09-13 11:07:06 +0800
---

Docker is great for quickly dropping into a Linux environment, but isn't compatible with certain obscure use cases (mine being testing version-locked Java GUIs).

After a period of unsuccessfully installing random packages and toggling flags, I figured the next-easiest thing to do was to use VirtualBox.
Perhaps surprisingly, it comes with an able CLI.
Here's how it compares to Docker's.

## Getting Started

```sh
brew install --cask virtualbox
```

There's no equivalent of `docker run -it` to _start a VM and give me a shell_; we'll have to use `ssh`.

<!--
https://www.howtogeek.com/122641/how-to-forward-ports-to-a-virtual-machine-and-use-it-as-a-server/
https://dev.to/developertharun/easy-way-to-ssh-into-virtualbox-machine-any-os-just-x-steps-5d9i
-->

We import the image, the equivalent of `docker load`. This takes about a minute, for a 4GB image.

```sh
vboxmanage import vm.ova

# `vm` from now on is the name of our virtual machine, which we can confirm with
vboxmanage list vms

# port forward, so we can use ssh. the first port is the host's
vboxmanage modifyvm vm --natpf1 "ssh,tcp,,2222,,22"

# power it on
vboxmanage startvm vm
vboxmanage startvm vm --type headless

# now it appears here
vboxmanage list runningvms

# wait for the VM to start, then
ssh -p 2222 user@127.0.0.1
```

At this point we can interactively get the VM into the state we want, or write a script to automate it. The subcommand for the latter is `guestcontrol`, similar to `docker exec`.

<!--
https://apple.stackexchange.com/questions/354985/best-way-to-run-shell-commands-on-virtualbox-guest
-->

```sh
vboxmanage guestcontrol vm run /bin/sh --username user --password pass --verbose --wait-stdout --wait-stderr -- -c "echo test"
```

The docs say that stdin is forwarded, but it seems signals aren't, so I couldn't get a piped shell script to run. We can work around that somewhat with the `guestcontrol copyto` subcommand.

```sh
vboxmanage guestcontrol vm copyto --verbose --username user --password pass host-dir --target-directory /home/vm
```

<!-- https://stackoverflow.com/questions/36662679/is-there-a-workaround-to-copy-files-to-a-vm -->

When we're done, we'll want to power the VM off, export the new state back to an ova file if necessary, then delete it.

```sh
vboxmanage controlvm vm poweroff
vboxmanage export vm -o vm1.ova
vboxmanage unregistervm vm --delete
```

## Mounted Volumes (aka Shared Folders)

<!--
https://askubuntu.com/questions/161759/how-to-access-a-shared-folder-in-virtualbox
https://ryansechrest.com/2012/10/permanently-share-a-folder-between-host-mac-and-guest-linux-os-using-virtualbox/
-->

I don't actually remember what the Guest Additions CD contributes to this, but it seems we don't need it here.

First, we tell VirtualBox about the shared folder. We'll have to power off for this.

```sh
vboxmanage sharedfolder add vm --name share --hostpath ~/Downloads/shared

# we see it here
vboxmanage showvminfo vm
```

Inside the VM, we get to pick where we want to mount the shared folder.

```sh
# create the directory we want to mount at
mkdir /home/user/shared

# add ourselves to the vboxsf group
sudo usermod -a -G vboxsf user

sudo mount -t vboxsf -o uid=$(id -u),gid=$(id -g),rw share /home/user/shared  
```

Powering the VM off unmounts the shared folder, but we can also do it manually.

```sh
sudo umount /home/user/shared
```

## Snapshots

I've not found many opportunities to use [docker checkpoint](https://docs.docker.com/engine/reference/commandline/checkpoint/), but [snapshots](https://docs.oracle.com/en/virtualization/virtualbox/6.0/user/vboxmanage-snapshot.html) get a special mention because they're a very useful part of VirtualBox, and the interface is nice and intuitive.

```sh
vboxmanage snapshot vm list
vboxmanage snapshot vm take s
vboxmanage snapshot vm restore s
vboxmanage snapshot vm delete s
```

## Verdict

Certainly not as easy as Docker, but it's FOSS and easy enough to automate. It's a great alternative if you just can't get Docker to work or need more isolation or reproducibility.

<!-- https://superuser.com/questions/584100/why-should-i-use-vagrant-instead-of-just-virtualbox -->
