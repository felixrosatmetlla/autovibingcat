from time import sleep
import os
import re
import asyncio

from atproto import AsyncClient, models

from autovibingcat import create_vibing_cat

# how often we should check for new notifications
FETCH_NOTIFICATIONS_DELAY_SEC = 10


async def main() -> None:
    async_client = AsyncClient()
    await async_client.login(os.environ['BSKY_VIBINGCAT_HANDLE'], os.environ['BSKY_VIBINGCAT_PASS'])

    # fetch new notifications
    while True:
        # save the time in UTC when we fetch notifications
        last_seen_at = async_client.get_current_time_iso()

        response = await async_client.app.bsky.notification.list_notifications()
        for notification in response.notifications:
            if not notification.is_read and notification.reason == 'mention':
                # TODO: Check that no response has been generated yet
                print('Received new request! Start processing it...')

                posts = await async_client.get_posts([notification.uri])
                post = posts.posts[0]

                txt = post.record.text
                x = re.search("@autovibingcat\.bsky\.social.*song:\"(.*)\".*start:[^0-9]+(\d+)", txt)
                songTitle = x[1]
                startTime = int(x[2])
                print(f'Request => song:{songTitle}; start:{startTime}')
                print('Start processing...')
                
                create_vibing_cat(songTitle, startTime)

                with open('temp_output/output.mp4', 'rb') as f:
                    vid_data = f.read()

                root_post_ref = models.create_strong_ref(post)
                try:
                    await async_client.send_video(text="Here is your video!", video=vid_data, reply_to=models.AppBskyFeedPost.ReplyRef(parent=root_post_ref, root=root_post_ref))
                except Exception as e:
                    await async_client.send_video(text="Here is your video!", video=vid_data, reply_to=models.AppBskyFeedPost.ReplyRef(parent=root_post_ref, root=root_post_ref))
        
        # mark notifications as processed (isRead=True)
        await async_client.app.bsky.notification.update_seen({'seen_at': last_seen_at})
        print('Successfully process notification. Last seen at:', last_seen_at)

        sleep(FETCH_NOTIFICATIONS_DELAY_SEC)


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())