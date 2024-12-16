from time import sleep
import os
import re
import asyncio

from atproto import Client, models

from autovibingcat import create_vibing_cat

# how often we should check for new notifications
FETCH_NOTIFICATIONS_DELAY_SEC = 10


async def main() -> None:
    client = Client()
    client.login(os.environ['BSKY_VIBINGCAT_HANDLE'], os.environ['BSKY_VIBINGCAT_PASS'])

    # fetch new notifications
    while True:
        # save the time in UTC when we fetch notifications
        last_seen_at = client.get_current_time_iso()

        response = client.app.bsky.notification.list_notifications()
        for notification in response.notifications:
            if not notification.is_read and notification.reason == 'mention':
                # TODO: Check that no response has been generated yet
                print('Received new request! Start processing it...')

                txt = "@autovibingcat.bsky.social song:\"Strategy - Twice\"; start:60"
                x = re.search("@autovibingcat\.bsky\.social song:\"(.*)\".*start:(\d+)", txt)
                songTitle = x[1]
                startTime = int(x[2])
                print(f'Request => song:{songTitle}; start:{startTime}')
                print('Start processing...')
                
                create_vibing_cat(songTitle, startTime)

                with open('temp_output/output.mp4', 'rb') as f:
                    vid_data = f.read()

                post = client.get_posts([notification.uri]).posts[0]
                root_post_ref = models.create_strong_ref(post)
                client.send_video(text="Here is your video!", video=vid_data, reply_to=models.AppBskyFeedPost.ReplyRef(parent=root_post_ref, root=root_post_ref))

                # example: "Got new notification! Type: like; from: did:plc:hlorqa2iqfooopmyzvb4byaz"

        # mark notifications as processed (isRead=True)
        # client.app.bsky.notification.update_seen({'seen_at': last_seen_at})
        print('Successfully process notification. Last seen at:', last_seen_at)

        sleep(FETCH_NOTIFICATIONS_DELAY_SEC)


if __name__ == '__main__':
    main()