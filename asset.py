class Asset:
    def __init__(self, id, name, category, value, status, assigned_to = None):
        self.id = id
        self.name = name
        self.category = category
        self.value = value
        self.status = status
        self.assigned_to = assigned_to

# Need to update this with any other required fields later on