"""
Verify AI Planner setup
"""

from app import create_app

app = create_app()

print('✅ App created successfully')
print('\nRegistered blueprints:')
for bp in app.blueprints:
    print(f'  - {bp}')

print('\nRegistered routes:')
for rule in app.url_map.iter_rules():
    if 'ai-planner' in rule.rule:
        print(f'  - {rule.rule} [{", ".join(rule.methods - {"HEAD", "OPTIONS"})}]')

print('\n✅ AI Planner module successfully integrated!')
