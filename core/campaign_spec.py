class CampaignSpec:

    def __init__(self,name,platform,budget,geo,interests,landing):
        self.name=name
        self.platform=platform
        self.budget=budget
        self.geo=geo
        self.interests=interests
        self.landing=landing

    def to_dict(self):
        return self.__dict__
