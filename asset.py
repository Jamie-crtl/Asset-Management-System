class Asset:
    ALLOWED_CATEGORIES = {"property", "vehicle", "other"}
    ALLOWED_STATUSES = {"available", "assigned", "disposed"}
    def __init__(self, id, name, category, value, status, assigned_to = None, history = None):
        category = str(category).strip().lower()
        status = str(status).strip().lower()

        if category not in Asset.ALLOWED_CATEGORIES:
            raise ValueError("Category must be one of the following values: property, vehicle, other")
        if status not in Asset.ALLOWED_STATUSES:
            raise ValueError("Status must be one of the following values: available, assigned, disposed")
        self.id = id
        self.name = name
        self.category = category # it , hardware , software
        self.value = value
        self.status = status
        self.assigned_to = assigned_to
        self.history = history if history is not None else []

# Need to update this with any other required fields later on