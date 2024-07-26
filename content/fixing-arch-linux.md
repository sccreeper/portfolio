Title: Fixing borked Arch Linux that uses btrfs
Summary: Sometimes it does this
Authour: Oscar Peace
Tags: Linux
      Guide
      Arch-Linux
Published: 26/7/2024

Sometimes after an update, my Arch linux install will no longer boot properly. This is usually because `mkinitcpio` failed or the GRUB config needed to be regenerated. This can be fixed by mounting the install with a `archlinux-chroot` however because I use btrfs with subvolumes, the process is a little different. This post mostly serves as a guide in order to help me out in the future and anyone else who has the same problem.

**Note:** This guide is written with the assumption that you have basic knowledge of the Linux command line and directory structure.

# Mounting steps

Firstly flash an [Arch ISO](https://archlinux.org/download/) to a USB stick and boot into it from your BIOS. Personally I like to just keep one around just incase this happens.

Once you have booted into the ISO, use `lsblk` to list the volumes and partitions available to your system. Find the **partition** that your system is installed on. It should look something like `/dev/sda1` or `/dev/nvme0n1p1`.

Then you have to mount the drives. If you have subvolumes then this is slightly different. If you don't then you can get away with doing this normally. The subvolume mount steps are below:

```shell
mount -o subvol=@ /dev/yourPartition /mnt/
mount -o subvol=@log /dev/yourPartition /mnt/var/log
mount -o subvol=@home /dev/yourPartition /mnt/home
mount -o subvol=@pkg /dev/yourPartition /mnt/var/cache/pacman/pkg
```

If the boot volume is on a separate partition then you have to mount that as well:

```shell
mount /dev/yourBootPartition /mnt/boot
```

You can ignore the "snapshots" volume.

Then you can chroot into the images and perform the subsequent steps to repair your system.

# Repair steps

If you know what you have to do to repair your system, you can skip this part.

Firstly chroot into the system in order to repair it:
```shell
arch-chroot /mnt
```

Then run the commands to repair the system. These may be different for you, however for me it consists of rerunning `mkinitcpio` and `grub-mkconfig` in order.

```
mkinitcpio -P
grub-mkconfig -o /boot/grub/grub.cfg
```

# Conclusion

Hopefully this helps you fix your system.
