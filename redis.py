import redis3

r = redis3.Redis(host='192.168.1.125', port=6379)
r.set('name', 'John')
print(r.get('name'))

r.sadd('cat','银渐层')
r.sadd('cat','美短')
r.sadd('cat','橘猫')
print(r.smembers('cat') )

r.sadd('dog','二哈')
r.sadd('dog','橘猫')
r.sadd('dog','柴犬')
print(r.smembers('dog'))

print(r.sdiff('cat','dog'))
print(r.sdiff('dog','cat'))

r.expire('dog',5)