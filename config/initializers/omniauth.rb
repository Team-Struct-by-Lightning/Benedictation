OmniAuth.config.logger = Rails.logger

GOOGLE_CONFIG = YAML.load_file("#{::Rails.root}/config/google.yml")[::Rails.env]

Rails.application.config.middleware.use OmniAuth::Builder do
  provider :google_oauth2, GOOGLE_CONFIG['app_id'], GOOGLE_CONFIG['secret'],
  {client_options: {ssl: {ca_file: Rails.root.join("cacert.pem").to_s}},
  access_type: 'offline', prompt: 'consent', scope: 'userinfo.email,calendar,drive, drive.file,drive.appdata, drive.apps.readonly'}
end