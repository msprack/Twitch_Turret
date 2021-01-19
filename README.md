# Twitch Turret - An IOT project where viewers can pay to blast a streamer.
Twitch Turret is a python script that interfaces with Twitch's API to monitor chat and fire an [automatic foam dart gun](https://www.walmart.com/ip/Adventure-Force-V-Twin-Motorized-Gatling-Belt-Dart-Blaster/787729752).
## Features
* Monitor Twitch chat for channel point redemption events and commands included with bitmoji cheers
* Randomly choose whether to fire based on given odds.
* Use GPIO pins to trigger [relays](https://www.amazon.com/gp/product/B07ZM84BVX/ref=as_li_tl?ie=UTF8&tag=msprack-20&camp=1789&creative=9325&linkCode=as2&creativeASIN=B07ZM84BVX&linkId=ad4f1cb6697d2757f26613ae99dca376) causing the automatic dart gun to fire.
* Use the twitch API to to clip the 30 second window around the firing of the dart gun.
* Use discord webhooks to post a link to the twitch clip to a discord server  
  
## [See this project in action](https://drive.google.com/file/d/1_cftDxLpTPuHTmL-ci7bYri_EEQSXF_N/view?usp=sharing)  
