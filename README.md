# Jupiter ♃
> internet relay chat botnet for efnet

![](.screens/jupiter.png)

*"let the battle of the +oooo -oooo commence"*

## Information
Jupiter will create a botnet by connecting a defined number of clones to every [EFNet](http://efnet.org) server. A single host could potentially create close to 100 clones without any suspicion. It is meant to monitor/jupe/hold nicks & be controlled to do just about anything.

For example, at the time of writing this, there are 12 active [EFNet](http://efnet.org) servers. With 3 clones per-server on IPv4 connections, plus another 3 clones per-server on IPv6 connections, thats 6 clones per-server, equating to 72 total clones...all from a single machine. Run this bot on multiple machines, you get the point.

Any server with SSL/TLS ports opened, will be connected using SSL/TLS. If using SSL/TLS to connect fails, it will fall back to a standard connection on port 6667 & will try an SSL/TLS again next time. When IPv6 is enabled, Servers with IPv6 support will be connected to with both IPv4 & IPv6 clones. Juping is handled using [MONITOR](https://ircv3.net/specs/extensions/monitor) to watch for nick changes or quits. The bots will also join a backup channel in-case the main channel gets killed & you need to find your bots. The backup channel is suffixed with random numbers & can be searched for from doing /LIST.

The bot is designed to be very minimal, secure, & trustless by nature. This means anyone can run a copy of your script on their server to help build your botnet.

It is highly recommended that you use a [random spoofing ident protocol daemon](https://github.com/internet-relay-chat/archive/blob/master/identd.py)

## Commands
| Command                | Description                                                                                                |
| ---------------------- | ---------------------------------------------------------------------------------------------------------- |
| `5000 <chan>`          | Emulates SuperNETs #5000 channel *(Join #5000 on irc.supernets.org for help using this command)*           |
| `id`                   | Send bot identity                                                                                          |
| `raw [-d] <data>`      | Send `<data>` to server, optionally delayed with -d argument                                               |
| `relay <chan>`         | Relay all data from `<chan>` into the bot channel *(Can not use @all & must join channel via `raw` first)* |
| `relay stop`           | Stop the relay *(Will not turn off from kicks, etc)*                                                       |
| `monitor list`         | Return MONITOR list                                                                                        |
| `monitor reset`        | Reset MONITOR list                                                                                         |
| `monitor <+/-><nicks>` | Add (+) or Remove (-) `<nicks>` from MONITOR list. *(Can be a single nick or comma seperated list)*        |
| `sync`                 | Sync the bot list *(Handled automatically but good practice to sync occasionally)*                         |

**Note:** All commands must be prefixed with `@all` or the bots nick & will work in a channel or private message.

Raw data must be [IRC RFC](https://www.rfc-editor.org/rfc/rfc2812) compliant data & any nicks in the **MONITOR** list will be juped as soon as they become available.

## EFNet Network Map
This is an accurate map of the [EFNet](http://efnet.org) IRC network as of *05/19/2023*:

| Host                         | DNS                                                        |
| ---------------------------- | ---------------------------------------------------------- |
| 128.39.65.230                | irc.underworld.no                                          |
| 130.226.213.194              | efnet.deic.eu                                              |
| 130.243.52.250               | irc.du.se                                                  |
| 185.100.59.59                | irc.efnet.nl                                               |
| 188.240.145.90               | irc.swepipe.se                                             |
| 195.140.202.142              | efnet.port80.se                                            |
| 195.159.90.90                | irc.homelien.no                                            |
| 198.47.99.99                 | irc.mzima.net                                              |
| 198.252.144.2                | irc.colosolutions.net                                      |
| 209.222.22.22                | irc.choopa.net                                             |
| 66.225.225.225               | irc.servercentral.net                                      |
| 67.218.118.62                | irc.Prison.NET                                             |
| 2001:16d8:aaaa:2::1338       | efnet.port80.se                                            |
| 2001:668:117::dead:beef:cafe | irc.mzima.net                                              |
| ~~2001:1838:1007::6667~~     | unknown or offline *(was in the irc.efnet.org roundrobin)* |
| 2001:19f0::dead:beef:cafe    | irc.choopa.net                                             |
| 2001:6b0:78::90              | irc.swepipe.se                                             |
| 2001:67c:12d8::6667          | irc.efnet.nl                                               |
| 2001:700:3100:1::babe        | irc.underworld.no                                          |
| 2001:840:0:1000:1::1         | irc.homelien.no                                            |
| 2001:878:0:e000:82:e2:d5:c2  | efnet.deic.eu                                              |
| ~~2001:948:7:7::139~~        | unknown or offline *(was in the irc.efnet.org roundrobin)* |

**Note:** Not every host is included in the *irc.efnet.org* roundrobin!

## Todo
- Ability to set admin/channel on the fly *(requested by delorean)*
- Built in identd server with randomized spoofing responses
- Improved protections *(Remove bans placed on bots, retaliate on KICK & +b)*
- Invite clones to +i channels
- Takeover attack features
- Possibly use only one connection per-server & create clones on `multiple` command / destroy clones on `destroy` command. *(No point in having clones when we arent doing anything with them)*
- Compile a list of common CTCP VERSION replies to improve the random CTCP VERSION responses
- WHO channel and parse unique hosts to +eI usage
- Polish the vhost/proxy support code *(was thrown together for chrono)* and add documentation about it.

___

###### Mirrors
[acid.vegas](https://git.acid.vegas/jupiter) • [GitHub](https://github.com/acidvegas/jupiter) • [GitLab](https://gitlab.com/acidvegas/jupiter) • [SuperNETs](https://git.supernets.org/acidvegas/jupiter)
