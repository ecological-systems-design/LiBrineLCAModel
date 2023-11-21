print(bd.methods)

m = bd.Method(('AWARE regionalized', 'Annual', 'All'))

test = bd.get_activity(m.load()[0][0]).as_dict()
print(test)

# Define your method
m = bd.Method(('AWARE regionalized', 'Annual', 'All'))

# Load the method to get a list of activities
activities = m.load()

# Loop through each activity in the list
for activity_tuple in activities :
    # Get the activity using the key from the tuple
    activity = bd.get_activity(activity_tuple[0])

    # Convert the activity to a dictionary and print it
    activity_dict = activity.as_dict()
    print(activity_dict)

# del bd.databases[site_name]
# del bd.databases[ei_name]