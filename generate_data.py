import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

def generate_data():
    # Set random seed for reproducibility
    random.seed(42)
    np.random.seed(42)

    # 500 users
    users = [f'U{str(i).zfill(3)}' for i in range(1, 501)]
    # 50 products
    products = [f'P{str(i).zfill(3)}' for i in range(1, 51)]

    actions = ['view', 'click', 'add_to_cart']
    action_weights = [0.6, 0.3, 0.1]

    data = []
    start_time = datetime.now() - timedelta(days=30)

    for user in users:
        # User behavior is a sequence of actions over a session or multiple sessions
        # 8 behaviours per user exactly
        num_behaviors = 8
        current_time = start_time + timedelta(minutes=random.randint(0, 40000))
        
        user_actions = []
        for _ in range(num_behaviors):
            # Sometimes a user adds to cart after viewing or clicking
            if len(user_actions) > 0 and user_actions[-1] == 'view' and random.random() < 0.3:
                action = 'click'
            elif len(user_actions) > 0 and user_actions[-1] == 'click' and random.random() < 0.4:
                action = 'add_to_cart'
            else:
                action = np.random.choice(actions, p=action_weights)
            
            user_actions.append(action)
            
            data.append({
                'user_id': user,
                'product_id': random.choice(products),
                'action': action,
                'timestamp': current_time.strftime("%Y-%m-%d %H:%M:%S")
            })
            current_time += timedelta(minutes=random.randint(1, 60))

    df = pd.DataFrame(data)
    df.to_csv('data_user500.csv', index=False)
    print(f"Dataset generated successfully with {len(df)} records for {len(users)} users.")
    print("Sample rows:")
    print(df.head())

if __name__ == "__main__":
    generate_data()
