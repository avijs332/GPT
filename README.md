# GPT
Generative Public Transportation Model with reinforcement learning

# Prerequisits

<ol>
pip install osmnx networkx pettingzoo gymnasium numpy matplotlib
</ol>

![f63cfe4c-5b2f-4386-ae3f-1b3bf95754bf](https://github.com/user-attachments/assets/30d9f155-2fda-4e05-9661-b8863701a675)

# Working with Remote server
## step 1
first you must install/ use the College vpn
so go [here](https://db.cs.colman.ac.il/downloads/SSL-VPN-Client-WIN.pdf), its a guide that explains how to connect and use it
for all the ips/passwords/and such... go to the mail that was sent by doron, its not safe to write it here. :(

## step 2
After activating the vpn

use `ssh` in the powershell to connect to the remote server, `ssh <inner ip>`. Now you are connected to the server!

## useful stuff
### screen
cool software to have 'multiple screens' in the terminal
#### start a screen
- `screen -S <tag>`
#### leave a screen
- ctrl + A + D
#### watch an existing screen
- `screen -r <tag>`
#### existing screens
- myapp: python server
- accessLog: nginx access log
