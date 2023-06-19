import os
import cv2
import json
import sqlite3
import pytesseract
import networkx as nx
from datetime import datetime
from collections import Counter
from transformers import pipeline
from polyglot.detect import Detector
from networkx.readwrite import json_graph

# DB connection
db = sqlite3.connect('hackforums.db')
cursor = db.cursor()



############
# LANGUAGE #-----
############

# lang = {}

# for it, post in enumerate(posts):

#     # print(post[header.index('originalPost')])

#     try:
#         detector = Detector(post[header.index('originalPost')])

#         try:
#             lang[str(detector.language).split(" ")[1]] += 1
#         except:
#             lang[str(detector.language).split(" ")[1]] = 1

#         # print("%s: %s" % (post[header.index('tid')], ))
#     except:
#         pass

# # Get all initially crawled posts
# cursor.execute('SELECT * FROM comments;')
# header = list(map(lambda x: x[0], cursor.description))
# posts = cursor.fetchall()

# comments = {}

# for it, post in enumerate(posts):

#     # print(post[header.index('originalPost')])

#     try:
#         detector = Detector(post[header.index('content')])

#         try:
#             comments[str(detector.language).split(" ")[1]] += 1
#         except:
#             comments[str(detector.language).split(" ")[1]] = 1

#         # print("%s: %s" % (post[header.index('tid')], ))
#     except:
#         pass

# # Stats
# print("Posts:")
# print(lang)
# print("Comments:")
# print(comments)





##################
# WORD FREQUENCY #-----
##################

# # Get all post names
# cursor.execute('SELECT name, originalPost FROM posts;')
# posts = cursor.fetchall()
# postNames = [el[0] for el in posts]
# postContents = [el[1] for el in posts]

# result = Counter()

# # Get word frequency
# for it, post in enumerate(posts):

#     # Remove special characters
#     list = []
#     for el in postNames[it].split():
#         normalizedWord = "".join(ch.lower() for ch in el if ch.isalnum())
#         if len(normalizedWord) > 1:
#             list.append(normalizedWord)
    
#     # Count words
#     result += Counter(list)

#     # Remove special characters
#     list = []
#     for el in postContents[it].split():
#         normalizedWord = "".join(ch.lower() for ch in el if ch.isalnum())
#         if len(normalizedWord) > 1:
#             list.append(normalizedWord)
    
#     # Count words
#     result += Counter(list)

# # Get all comments
# cursor.execute('SELECT content FROM comments;')
# comments = cursor.fetchall()

# # Get word frequency
# for comment in comments:

#     # Remove special characters
#     list = []
#     for el in comment[0].split():
#         normalizedWord = "".join(ch.lower() for ch in el if ch.isalnum())
#         if len(normalizedWord) > 1:
#             list.append(normalizedWord)
    
#     # Count words
#     result += Counter(list)





################
# POST BY DATE #-----
################

# # Get all initially crawled posts
# cursor.execute('SELECT * FROM posts;')
# header = list(map(lambda x: x[0], cursor.description))
# posts = cursor.fetchall()

# day = {}
# month = {}
# year = {}

# for it, post in enumerate(posts):

#     if post[header.index('creation')] != 'creation':
#         creationDate = str(datetime.fromtimestamp(float(post[header.index('creation')])).strftime("%d/%m/%Y"))
#         creationMonth = str(datetime.fromtimestamp(float(post[header.index('creation')])).strftime("%m/%Y"))
#         creationYear = str(datetime.fromtimestamp(float(post[header.index('creation')])).strftime("%Y"))

#     try:
#         day[creationDate] += 1
#     except:
#         day[creationDate] = 1

#     try:
#         month[creationMonth] += 1
#     except:
#         month[creationMonth] = 1

#     try:
#         year[creationYear] += 1
#     except:
#         year[creationYear] = 1

# # Stats
# print("Date:")
# print(day)

# print("Month:")
# print(month)

# print("Year:")
# print(year)

# # Get all initially crawled posts
# cursor.execute('SELECT * FROM comments;')
# header = list(map(lambda x: x[0], cursor.description))
# posts = cursor.fetchall()

# day = {}
# month = {}
# year = {}

# for it, post in enumerate(posts):

#     if post[header.index('date')] == '0':
#         print(post[header.index('commentId')])
#         exit()

#     creationDate = str(datetime.fromtimestamp(float(post[header.index('date')])).strftime("%d/%m/%Y"))
#     creationMonth = str(datetime.fromtimestamp(float(post[header.index('date')])).strftime("%m/%Y"))
#     creationYear = str(datetime.fromtimestamp(float(post[header.index('date')])).strftime("%Y"))

#     try:
#         day[creationDate] += 1
#     except:
#         day[creationDate] = 1

#     try:
#         month[creationMonth] += 1
#     except:
#         month[creationMonth] = 1

#     try:
#         year[creationYear] += 1
#     except:
#         year[creationYear] = 1

# # Stats
# print("Date:")
# print(day)

# print("Month:")
# print(month)

# print("Year:")
# print(year)





#######
# OCR #-----
#######

# # Load images
# for img in os.listdir("images"):

#     try:
#         file = os.path.join("images", img)
#         image = cv2.imread(file, cv2.IMREAD_GRAYSCALE)

#         # Preprocess image
#         image = cv2.resize(image, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
#         image = cv2.medianBlur(image, 3)

#         # Perform OCR
#         text = pytesseract.image_to_string(image)
#         values = [text, img.split("-")[0]]

#         # Print recognized text
#         print("OK: %s" % img)
#         db.execute("UPDATE posts SET imgData = ? WHERE tid = ?", values)
#         db.commit()
#     except:
#         values = ["no data", img.split(".")[0]]
#         print("ERROR: %s" % img)
#         db.execute("UPDATE posts SET imgData = ? WHERE tid = ?", values)
#         db.commit()





#############
# RELATIONS #-----
#############

# G = nx.DiGraph()

# # Get all users
# cursor.execute('SELECT id, name FROM users WHERE popularity > 1;')
# users = cursor.fetchall()

# # Add node
# userNames = [user[1] for user in users]
# aux = [user[0] for user in users]
# users = [user[0] for user in users]
# nodes = [(user, {"kind": "commenter", "name": userNames[it]}) for it, user in enumerate(users)]

# # Get top posts
# cursor.execute('SELECT * FROM posts ORDER BY views DESC;')# LIMIT 100
# postHeader = list(map(lambda x: x[0], cursor.description))
# posts = cursor.fetchall()

# # Add node
# nodes += [(post[postHeader.index('tid')], {"kind": "post", "name": post[postHeader.index('name')]}) for post in posts]

# # Get links between users and posts
# links = []
# for it, post in enumerate(posts):
#     print("%s/%s" % (it, len(posts)), end="\r")

#     # If post is closed
#     closed = ['closed', 'paused', 'deleted', 'removed']
#     if any([x in post[postHeader.index('name')].lower() for x in closed]):
#         nodes[[y[0] for y in nodes].index(post[postHeader.index('tid')])] = (post[postHeader.index('tid')], {"kind": "closed", "name": post[postHeader.index('name')]})

#     # Get all comments from post
#     cursor.execute('SELECT count(*) as count, userUid FROM comments WHERE postId = %s GROUP BY userUid;' % post[postHeader.index('tid')])
#     commentHeader = list(map(lambda x: x[0], cursor.description))
#     comments = cursor.fetchall()

#     for comment in comments:
#         # Is the comment by one of the saved users?
#         if comment[commentHeader.index('userUid')] in users:
#             # If user is creator of post
#             if comment[commentHeader.index('userUid')] == post[postHeader.index('creatorUid')]:
#                 nodes[[y[0] for y in nodes].index(comment[commentHeader.index('userUid')])] = (comment[commentHeader.index('userUid')], {"kind": "creator", "name": nodes[[y[0] for y in nodes].index(comment[commentHeader.index('userUid')])][1]["name"]})
#                 links.append((comment[commentHeader.index('userUid')], post[postHeader.index('tid')], {'count': comment[commentHeader.index('count')], 'kind': 'creation'}))
#             # If user is commenter
#             else:
#                 links.append((comment[commentHeader.index('userUid')], post[postHeader.index('tid')], {'count': comment[commentHeader.index('count')], 'kind': 'comment'}))
            
#             # Remove from aux list
#             try:
#                 aux.pop(aux.index(comment[commentHeader.index('userUid')]))
#             except:
#                 pass

# # Delete users not connected to top100
# for user in aux:
#     nodes.pop([y[0] for y in nodes].index(user))

# # Save relations
# G.add_nodes_from(nodes)
# G.add_edges_from(links)
# degree = nx.degree_centrality(G)
# betweenness = nx.betweenness_centrality(G)
# closeness = nx.closeness_centrality(G)

# # Prepare json
# graph_data = json_graph.node_link_data(G)
# for index, node in enumerate(graph_data['nodes']):
#     node_id = graph_data['nodes'][index]['id']
#     graph_data['nodes'][index]['degree'] = degree.get(node_id, 0)
#     graph_data['nodes'][index]['betweenness'] = betweenness.get(node_id, 0)
#     graph_data['nodes'][index]['closeness'] = closeness.get(node_id, 0)

# json.dump(graph_data, open("data.json", "w"), ensure_ascii=False)







#########
# USERS #-----
#########

# # Get all users
# cursor.execute('SELECT id FROM users;')
# users = cursor.fetchall()
# users = [user[0] for user in users]

# oneComment = 0
# nComment = 0

# oneCreate = 0
# nCreate = 0

# oneCreateOneComment = 0
# nCreateOneComment = 0
# oneCreateNComment = 0
# nCreateNComment = 0

# for it, user in enumerate(users):
#     print("%s/%s" % (it, len(users)), end="\r")
#     cursor.execute('SELECT count(*), postId FROM comments WHERE userUid = %s GROUP BY postId;' % user)
#     comments = cursor.fetchall()

#     cursor.execute('SELECT count(*) FROM posts WHERE creatorUid = %s;' % user)
#     posts = cursor.fetchall()

#     if posts[0][0] == 0:
#         if len(comments) == 1:
#             oneComment += 1
#         else:
#             nComment += 1
#     else:
#         if len(comments) == 0:
#             if posts[0][0] == 1:
#                 oneCreate += 1
#             else:
#                 nCreate += 1
#         elif len(comments) == 1:
#             if posts[0][0] == 1:
#                 oneCreateOneComment += 1
#             else:
#                 nCreateOneComment += 1
#         else:
#             if posts[0][0] == 1:
#                 oneCreateNComment += 1
#             else:
#                 nCreateNComment += 1

# print("oneComment: %d"%oneComment)
# print("nComment: %d"%nComment)
# print("oneCreate: %d"%oneCreate)
# print("nCreate: %d"%nCreate)
# print("oneCreateOneComment: %d"%oneCreateOneComment)
# print("nCreateOneComment: %d"%nCreateOneComment)
# print("oneCreateNComment: %d"%oneCreateNComment)
# print("nCreateNComment: %d"%nCreateNComment)





##################
# GRAPH ANALYSIS #-----
##################
# # Get in-degree
# cursor.execute('SELECT count(commentId), postId FROM comments WHERE userUid != (SELECT creatorUid FROM posts WHERE tid = postId limit 1) GROUP BY postId;')
# count = cursor.fetchall()
# comments = [el[0] for el in count]
# tids = [el[1] for el in count]

# cursor.execute('SELECT tid, creatorUid FROM posts;')
# count = cursor.fetchall()
# posts = [el[0] for el in count]
# users = [el[1] for el in count]

# result = {}
# for it, user in enumerate(users):
#     if posts[it] in tids:
#         try:
#             result[user]["in"] += comments[tids.index(posts[it])]
#         except:
#             result[user] = {}
#             result[user]["in"] = comments[tids.index(posts[it])]
#             result[user]["out"] = 0

# # Get out-degree
# cursor.execute('SELECT count(commentId), userUid FROM comments WHERE userUid != (SELECT creatorUid FROM posts WHERE tid = postId limit 1) GROUP BY userUid;')
# count = cursor.fetchall()
# comments = [el[0] for el in count]
# users = [el[1] for el in count]

# for it, user in enumerate(users):
#     try:
#         result[user]["out"] += comments[it]
#     except:
#         result[user] = {}
#         result[user]["out"] = comments[it]
#         result[user]["in"] = 0

# for user in result:
#     result[user]['degree'] = result[user]["in"] + result[user]["out"]

# cursor.execute('SELECT id, popularity FROM users WHERE popularity;')
# count = cursor.fetchall()

# # Degree x Popularity sorted by popularity
# count = sorted(count, key=lambda x: x[1])
# users = [el[0] for el in count]
# popularity = [el[1] for el in count]

# for it, user in enumerate(users):
#     try:
#         print("User: %s" % user)
#         print("In-degree: %s" % result[user]["in"])
#         print("Out-degree: %s" % result[user]["out"])
#         print("Popularity: %s" % popularity[it])
#     except:
#         pass
#     print()

# # Degree x Popularity sorted by degree
# users = [el[0] for el in count]
# popularity = [el[1] for el in count]

# inList = []
# outList = []
# for el in result:
#     inList.append((el, result[el]['in']))
#     outList.append((el, result[el]['out']))

# inList = sorted(inList, key=lambda x: x[1])
# outList = sorted(outList, key=lambda x: x[1])


# for it, user in enumerate(inList):
#     try:
#         print("User: %s" % user[0])
#         print("In-degree: %s" % user[1])
#         print("Out-degree: %s" % result[user[0]]['out'])
#         print("Popularity: %s" % popularity[users.index(user[0])])
#     except:
#         pass
#     print()





###############
# EIGENVECTOR #-----
###############
# import networkx as nx

# G = nx.DiGraph()

# # Get all users
# cursor.execute('SELECT id, name, popularity FROM users WHERE popularity > 1;')
# users = cursor.fetchall()

# # Add node
# userNames = [user[1] for user in users]
# popularity = [user[2] for user in users]
# aux = [user[0] for user in users]
# users = [user[0] for user in users]
# nodes = [(user, {"kind": "commenter", "name": userNames[it]}) for it, user in enumerate(users)]

# # Get top posts
# cursor.execute('SELECT * FROM posts ORDER BY views DESC LIMIT 100;')
# postHeader = list(map(lambda x: x[0], cursor.description))
# posts = cursor.fetchall()
# tids = [post[0] for post in posts]
# names = [post[1] for post in posts]
# views = [post[6] for post in posts]

# # Add node
# nodes += [(post[postHeader.index('tid')], {"kind": "post", "name": post[postHeader.index('name')]}) for post in posts]

# # Get links between users and posts
# links = []
# for it, post in enumerate(posts):
#     print("%s/%s" % (it, len(posts)), end="\r")

#     # If post is closed
#     closed = ['closed', 'paused', 'deleted', 'removed']
#     if any([x in post[postHeader.index('name')].lower() for x in closed]):
#         nodes[[y[0] for y in nodes].index(post[postHeader.index('tid')])] = (post[postHeader.index('tid')], {"kind": "closed", "name": post[postHeader.index('name')]})

#     # Get all comments from post
#     cursor.execute('SELECT count(*) as count, userUid FROM comments WHERE postId = %s GROUP BY userUid;' % post[postHeader.index('tid')])
#     commentHeader = list(map(lambda x: x[0], cursor.description))
#     comments = cursor.fetchall()

#     for comment in comments:
#         # Is the comment by one of the saved users?
#         if comment[commentHeader.index('userUid')] in users:
#             # If user is creator of post
#             if comment[commentHeader.index('userUid')] == post[postHeader.index('creatorUid')]:
#                 nodes[[y[0] for y in nodes].index(comment[commentHeader.index('userUid')])] = (comment[commentHeader.index('userUid')], {"kind": "creator", "name": nodes[[y[0] for y in nodes].index(comment[commentHeader.index('userUid')])][1]["name"]})
#                 links.append((comment[commentHeader.index('userUid')], post[postHeader.index('tid')], {'count': comment[commentHeader.index('count')], 'kind': 'creation'}))
#             # If user is commenter
#             else:
#                 links.append((comment[commentHeader.index('userUid')], post[postHeader.index('tid')], {'count': comment[commentHeader.index('count')], 'kind': 'comment'}))
            
#             # Remove from aux list
#             try:
#                 aux.pop(aux.index(comment[commentHeader.index('userUid')]))
#             except:
#                 pass

# # Delete users not connected to top100
# for user in aux:
#     nodes.pop([y[0] for y in nodes].index(user))

# # Save relations
# G.add_nodes_from(nodes)
# G.add_edges_from(links)

# eigenvector = nx.eigenvector_centrality(G)
# aux = {}
# for key in eigenvector:
#     if eigenvector[key] != 2.6612773599898427e-05:
#         aux[key] = eigenvector[key]
# eigenvector = aux
# sortedEigenvector = sorted(eigenvector.items(), key=lambda x:x[1])

# for user in sortedEigenvector:
#     try:
#         print("Post: %s" % names[tids.index(user[0])])
#         print("Eigenvector: %s" % user[1])
#         print("Views: %s" % views[tids.index(user[0])])
#     except:
#         pass
#     print()






###############
# OFFER POSTS #-----
###############
# # Get nComments
# cursor.execute('SELECT count(*) FROM posts;')
# count = cursor.fetchall()
# comments = count[0][0]

# # Get offers
# offers = []
# keywords = ['help', 'need', 'advice', 'advise', 'request', 'question', 'looking for', 'doubt', 'seeking']
# for keyword in keywords:
#     # cursor.execute('SELECT tid FROM posts WHERE originalPost LIKE "%' + keyword + '%";')
#     cursor.execute('SELECT name FROM posts WHERE name LIKE "%' + keyword + '%";')
#     count = cursor.fetchall()
#     results = [el[0] for el in count]
#     print(results)

#     for result in results:
#         if result not in offers:
#             offers.append(result)

# print(comments)
# print(len(offers))


db.close()