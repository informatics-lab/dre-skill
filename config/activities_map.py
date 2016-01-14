activities_map = {
	'run': ['run', 'jog', 'running', 'jogging'],
	'sunbathe': ['sunbathe', 'sunbathing']
}

activities = dict((i, k) for k in activities_map for i in activities_map[k])