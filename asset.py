class Asset:
    def __init__(self, id, name, category, value, status, assigned_to = None):
        ALLOWED_CATEGORIES = {"property","vehicle","other"}
        ALLOWED_STATUSES = {"available", "assigned","disposed"}

        if category not in ALLOWED_CATEGORIES:
            raise ValueError("Category must be one of the following values: property, vehicle, other")
        if status not in ALLOWED_STATUSES:
            raise ValueError("Status must be one of the following values: available, assigned, disposed")
        self.id = id
        self.name = name
        self.category = category # it , hardware , software
        self.value = value
        self.status = status
        self.assigned_to = assigned_to

# Need to update this with any other required fields later on