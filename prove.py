import redis

r = redis.Redis(
    host="redis-19972.c300.eu-central-1-1.ec2.cloud.redislabs.com",
    port="19972",
    password="NgAd1ouoICZTBouwpkWjCzPm2YUE0GBS",
)

r.sadd("sonounachiave","sonovalore 1")
compagni = ["ciao","sos", "WOWOOWOWO"]
r.sadd("sonounachiave", [x for x in compagni])

print(r.smembers("sonounachiave"))
