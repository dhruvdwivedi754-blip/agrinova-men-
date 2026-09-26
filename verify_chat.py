import os
os.chdir(r'c:/Users/dhruv/Downloads/Agrinova-main/Agrinova-main/AgriNova_OneSite')
import app
print('GEMINI_API_KEY_SET', bool(os.getenv('GEMINI_API_KEY')))
print('GEMINI_REPLY')
print(app.gemini_reply('How can I control pests in wheat?'))
print('RULE_REPLY')
print(app.rule_based_reply('How can I control pests in wheat?'))
