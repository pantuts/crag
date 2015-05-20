# crag
PoC craiglist flagging bot.

###### Note: This is only a PoC.

##### Agreement: This script is for educational purposes only. By using this script you agree that you alone will be responsible for any act you make. The author will not be liable of your actions.

```
Usage: python2.7 crag.py links.txt proxies.txt
```

The logic of bot:
* The script check for proxy if working.
* 5 threads per proxy per url.
* Starts flagging, loop flagging if still not flagged.
* Change proxy after successful flags.
* If proxy reaches error connection/timeout of 20 tries, change proxy then remove dead proxy.
* Continue until completion of links.
