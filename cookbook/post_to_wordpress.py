from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import GetPosts, NewPost
from wordpress_xmlrpc.methods.users import GetUserInfo
wp = Client('http://127.0.0.1/wordpress/xmlrpc.php', 'lotaku', 'qQ2@wW')
a = wp.call(GetPosts())


#wp.call(GetUserInfo())

post = WordPressPost()
post.title = 'My new title'
post.content = 'This is the body of my new post.'
post.terms_names = {
  'post_tag': ['test', 'firstpost'],
  'category': ['Introductions', 'Tests']
}
post.
# a = wp.call(NewPost(post))
print "xx"
# print a
print dir(post)