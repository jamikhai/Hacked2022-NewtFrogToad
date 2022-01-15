import requests
import os
import json
import shutil
import datetime as dt

# To set your environment variables in your terminal run the following line:
# export 'BEARER_TOKEN'='<your_bearer_token>'
bearer_token = os.environ.get("BEARER_TOKEN")

search_url = "https://api.twitter.com/2/tweets/search/recent"

# Range of last 7 days in ISO
date_list = [(dt.datetime.utcnow().replace(microsecond=0) - dt.timedelta(days=x)).isoformat() + 'Z' for x in range(7)]
# Request has to be at least 10 seconds before current time
date_list[0] = (dt.datetime.utcnow().replace(microsecond=0) - dt.timedelta(seconds=30)).isoformat() + 'Z'

# Optional params: start_time,end_time,since_id,until_id,max_results,next_token,
# expansions,tweet.fields,media.fields,poll.fields,place.fields,user.fields
query_params = {'query': '#BoredApeYC',
                'expansions': 'author_id',
                'tweet.fields': ['author_id'],
                'max_results': 100,
                'user.fields': 'profile_image_url',
                'end_time': date_list[0] # Default to today
                }

def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """

    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2RecentSearchPython"
    return r

def connect_to_endpoint(url, params):
    response = requests.get(url, auth=bearer_oauth, params=params)
    #print(response.status_code)
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return response.json()


def main():
    # Want to get tweets from each day of the past 7 days
    initial_no_images = len(os.listdir("./images"))
    counter = 0
    for i in range(len(date_list)):
        # Change the date each time
        query_params['end_time'] = date_list[i]
        json_response = connect_to_endpoint(search_url, query_params)
        json_dict = json_response
        #json_dict = json.dumps(json_response, indent=4, sort_keys=True)

        # Get all profile picture links that are not default images (likely apes)
        img_links = []
        for user in json_dict["includes"]["users"]:
            img_url = user["profile_image_url"]
            if "default_profile_images" not in img_url:
                img_links.append(img_url)

        print(f"Day: {date_list[i]}")
        print(f"Number of Links: {len(img_links)}")

        # Save each image in images folder
        for url in img_links:
            img_name = url.split('/')[-1]
            r = requests.get(url, stream=True)

            if r.status_code == 200:
                r.raw.decode_content = True

                with open (f"./images/{img_name}", 'wb') as f:
                    shutil.copyfileobj(r.raw, f)
                #print(f"Image successfully downloaded: {img_name}")
                counter += 1
            else:
                print("Error getting image")

    print(f"Images downloaded: {counter}")
    final_no_images = len(os.listdir("./images"))
    print(f"New images: {final_no_images - initial_no_images}")
    print(f"Current Number of images: {final_no_images}")


if __name__ == "__main__":
    ""
    main()