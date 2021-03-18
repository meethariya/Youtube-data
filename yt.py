from googleapiclient.discovery import build
from difflib import get_close_matches 
import mysql.connector as SQL


API_KEY = 'Your_Google_Youtube_Data_Api_V3_Key'
# youtube channel id of WIT PLC community
CHANNEL_ID='UCb9okJF6NGPDUGgAQxu3TcA'


def passer(vi,addi):
    # a general funtion to get likes ,dislikes , etc. attribute as passed to it
    # returns count of passed attribute , if any error returns none
    try:
        attribute = int(vi['statistics'][addi+'Count'])
    except Exception:
        attribute = None
    return attribute


channel = build('youtube', 'v3', developerKey=API_KEY)
pl_nextpagetoken,counter,records = None,1,[]

# list of department name to ignore change in spelling
dept_pattern = ['Civil Engineering', 'Mechanical Engineering', 'Electronics and Telecommunication', 'Electronics Engineering','Information Technology','Computer Science & Engineering','Humanities and Sciences','E&TC']
while True:
    # retrives all playlists of a channel
    pl_request = channel.playlists().list(
            part = 'snippet,contentDetails',
            channelId = CHANNEL_ID,
            maxResults = 50,
            pageToken = pl_nextpagetoken 
        )
    pl_response = pl_request.execute()
    for item in pl_response['items']:
        vis_nextpagetoken = None
        pl_id = item['id']
        pl_name = item['snippet']['title']
        # retrives information of particular playlist
        vis_request = channel.playlistItems().list(
            part = 'contentDetails',
            playlistId = pl_id,
            maxResults = 50
        )
        vis_response = vis_request.execute()

        # retrives list of all videos
        for vis in vis_response['items']:
            vi_id = vis['contentDetails']["videoId"]
            vi_request = channel.videos().list(
                part = 'snippet,statistics',
                id = vi_id
            )
            vi_response = vi_request.execute()


            # retrives info of particular video
            for vi in vi_response['items']:
                # gets name of video
                video_name = vi['snippet']['title']
                description = vi['snippet']['description']
                description = description.split('\n')
                # link of that video by concating with video id
                link="https://www.youtube.com/watch?v="+vi['id']
                dept_name=None


                # using description to get teacher name, and department name
                for i in description:
                    # clears typing error for department name by matching most accurate
                    dept_name = get_close_matches(i, dept_pattern,n=1,cutoff=0.4)
                    if dept_name:
                        dept_name=dept_name[0]
                        break
                # if department name not found returns unavailable
                if not dept_name:
                    dept_name='UNAVAILABLE'
                elif dept_name == 'E&TC':
                    dept_name = 'Electronics and Telecommunication'
                # try finding teacher name if not found returns unavailable
                try:
                    teacher_name=description[0]
                except Exception:
                    teacher_name = 'Unavailable'
                # gets view count of video
                views = passer(vi,'view')
                #gets like count of video
                likes = passer(vi,'like')
                # gets dislikes count of video
                dislikes = passer(vi,'dislike')
                # gets comment count of video
                comments = passer(vi,'comment')
                

                # stores all information as tuple and adding to list of records
                record=tuple([counter,pl_name,video_name,teacher_name,link,dept_name,likes,dislikes,views,comments])
                records.append(record)
                # printing video number count
                print(f"video number:- {counter}")
                counter+=1
    pl_nextpagetoken = pl_response.get('nextPageToken')
    # exit when no page available
    if not pl_nextpagetoken:
        break


#connecting to database named "sample"
conn=SQL.connect(host='localhost',user='root',passwd='',database='sample')
cur=conn.cursor()
cur.executemany("INSERT INTO videos VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);",records)
conn.commit()
conn.close()
