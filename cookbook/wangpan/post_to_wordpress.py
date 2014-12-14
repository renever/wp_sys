from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import GetPosts, NewPost
from wordpress_xmlrpc.methods.users import GetUserInfo

wp = Client('http://95.211.60.76/xmlrpc.php', 'l', 'jpqQ2@wW')
a = wp.call(GetPosts())


#wp.call(GetUserInfo())

post = WordPressPost()
post.title = 'My new title6'
post.content = 'This is the body of my new post.'
post.post_status = 'publish'
post.terms_names = {
  'post_tag': ['test', 'firstpost'],
  'category': ['Introductions', 'Tests'],
  # 'publish':'publish'
}

a = wp.call(NewPost(post))
print "xx"
# print a
print dir(post)