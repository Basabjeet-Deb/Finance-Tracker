"""
Service for generating contextual deals and gamification based on user spending.
It uses a free, local rule-based approach to match realistic active coupons to users.
"""

class DealsService:
    # Static database of contextual deals (simulating an affiliate API for free)
    ACTIVE_DEALS = {
        "Food": [
            {"merchant": "Swiggy", "code": "SWIGGYIT", "description": "Flat ₹150 off on Food Delivery above ₹400"},
            {"merchant": "Zomato", "code": "ZOMATO50", "description": "50% off up to ₹100 on your next meal"}
        ],
        "Transport": [
            {"merchant": "Uber", "code": "UBER25", "description": "25% off on your next 3 rides"},
            {"merchant": "Ola", "code": "OLAAUTO", "description": "Flat ₹20 off on Auto rides"}
        ],
        "Lifestyle": [
            {"merchant": "Myntra", "code": "MYNTRA200", "description": "Flat ₹200 off on fashion apparel"},
            {"merchant": "BookMyShow", "code": "BMS50", "description": "50% off on second movie ticket"}
        ],
        "Shopping": [
            {"merchant": "Amazon", "code": "AMZN10", "description": "10% cashback on Amazon Pay ICICI"},
            {"merchant": "Flipkart", "code": "FLIPKARTPLUS", "description": "Free early access to all sales"}
        ]
    }

    @staticmethod
    def get_deals_for_user(spending_aggregate: dict) -> list:
        """
        Analyze the user's spending array and return matching gamified deals.
        spending_aggregate is a dict of category -> amount spent.
        """
        recommended_deals = []
        
        # Sort categories by highest spend
        sorted_categories = sorted(spending_aggregate.items(), key=lambda x: x[1], reverse=True)
        
        for category, amount in sorted_categories:
            if amount > 1000: # Gamification logic: Only show deals if they spend actively in a category
                if category in DealsService.ACTIVE_DEALS:
                    # Provide the best deal for their top spending category
                    recommended_deals.append({
                        "category_trigger": category,
                        "spend_amount": amount,
                        "deal": DealsService.ACTIVE_DEALS[category][0]
                    })
            if len(recommended_deals) >= 2: # Keep it limited to top 2 deals so it's not spammy
                break
                
        return recommended_deals
