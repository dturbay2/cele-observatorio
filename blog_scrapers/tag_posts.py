"""
To run:
> python tag_posts.py <platform>

`platform` argument can be one of: fb, twitter, google

Edit `category_map`, and `found_key_term` function for more sophisticated 
clasification
"""
import json
import pandas as pd
import re
import sys

category_map = {
    'hate_speech': [
        "hate speech",
        "hate",
        "racism",
        "discrimination",
        ],
    'children': [
        "children",
        "children safety",
        ],
    'health_disinfo': [
        "disinformation",
        "misinformation",
        "public health",
        "health",
        "patients",
        ],
    'political_disinfo': [
        "disinformation",
        "misinformation",
        "elections",
        "electoral campaigns",
        "candidates",
        ],
    'gender_violence': [
        "violence against women",
        "safety of women online",
        "gender violence",
        ],
    'safety': [
        "safe",
        "safety",
        "safe Internet",
        ],
}

distance = 100  # number of characters allowed between regex terms
regex_category_map = {
    'hate_speech': [
        r'(hate|racist|discrimination|bigoted).{0,' + r'{}'.format(distance) + r'}speech',
        ],
    'children': [
        r'child(ren)?.{0,' + r'{}'.format(distance) + r'}safe(ty)?',
        ],
    'health_disinfo': [
        r'(public\s)?health.{0,' + r'{}'.format(distance) + r'}(mis|dis)info(rmation)?',
        ],
    'political_disinfo': [
        r'politic(al|s).{0,' + r'{}'.format(distance) + r'}(mis|dis)info(rmation)?',
        ],
    'gender_violence': [
        r'(gender|woman|women).{0,' + r'{}'.format(distance) + r'}violence',
        ],
    'safety': [
        r'(internet)?.{0,' + r'{}'.format(distance) + r'}safe(ty)?',
        ],
}

_PLATFORMS = ['fb', 'google', 'twitter']

def posts_to_df(json_path):
    '''convests json file of detailed blogposts to a pandas DataFrame'''
    with open(json_path) as f:
        lines = f.read().splitlines()
    data = [json.loads(line) for line in lines]
    return pd.DataFrame.from_dict(data, orient='columns')


def found_key_term(text, term, match_type):
    '''
    returns boolean if `term` is found in `text`. `match_type` can be 'simple'
    or 'regex' based on the category mapping values
    '''
    if match_type == 'simple':
        return term in text
    elif match_type == 'regex':
        return re.search(term, text, flags=re.IGNORECASE) is not None


def categorize_post(post_text, category_map, match_type='regex'):
    '''returns a set of matched categories for a blog posts'''
    matched_categories = []
    for category, key_terms in category_map.items():
        for term in key_terms:
            if found_key_term(post_text, term, match_type) and category not in matched_categories:
                matched_categories.append(category)
    return matched_categories


def output_classified_list(platform, category_map, explode_categories=True):
    '''
    categorizes a platforms blog posts based on `category_map`
    - `platform`: must be one of  `fb`, `twitter`, or `google`
    - `category_map`: dictionary of categories and key terms
    - `explode_categories`: flag makes an indicator column for each category 
       found in the dataset

    Outputs a df with classification based on category map, without the text
    from the blog post.
    '''
    assert platform in _PLATFORMS, '`platform` must be: fb, twitter, or google'
    file_path = 'output/{platform}_detailed.json'
    df = posts_to_df(file_path.format(platform=platform))
    df['categories'] = df['post_text'].apply(
        lambda post: categorize_post(post, category_map)
        )
    df.drop(columns=['post_text'], inplace=True)
    if explode_categories:
        category_columns = pd.get_dummies(df.categories.explode())
        category_columns = category_columns.groupby(level=0).sum()
        df = pd.concat([df, category_columns], axis=1)
    return df


if __name__ == '__main__':
    platform = sys.argv[1]    
    output_file = f'output/{platform}_summary_tagged.csv'
    df = output_classified_list(platform, regex_category_map)
    print(f'Writing categorized {platform} posts to {output_file}')
    df.to_csv(output_file)
