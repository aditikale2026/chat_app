import redis 

r = redis.Redis(
    host="localhost",
    port=6379,
    db=0,
    decode_responses=True  # gives string instead of bytes
)

r.set("name", "Aditi")
print(r.get("name"))  # Aditi

r.hset("user1",mapping={
    "name":'aditi',
    "age":22
})

print(r.hgetall("user1"))


r.rpush("tasks", "task1","task2")
print(r.lrange("tasks",0,-1))
