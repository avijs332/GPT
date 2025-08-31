# GPT
Generative Public Transportation Model with reinforcement learning

GPT focuses on developing a city-specific planning model for optimizing public transportation routes using Multi-Agent Proximal Policy Optimization (MAPPO). The primary objective is to provide city planners and mayors with data-driven tools to design efficient public transport lane layouts that maximize coverage, reduce travel times, and ensure accessibility to key points of interest across the city.


![519c5cb4-98da-42d0-b569-19421c208168 (1)](https://github.com/user-attachments/assets/dd66c524-c95b-4be0-84ea-ec35aa92763a)

<img width="1590" height="590" alt="image" src="https://github.com/user-attachments/assets/2044745b-cf91-40cc-befe-bb8d9af9125f" />


# Prerequisits

pettingzoo
osmnx
networkx
imageio
matplotlib
numpy
tensorflow
keras

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

## Upload files
So to upload files to the remote, you must use the sftp protocol. I found the vscode sftp extension to be the easiest option, you are welcome to use whatever you want. But remember that ssh and sftp are the only supported protocols!

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
- app: python server
- accessLog: nginx access log
