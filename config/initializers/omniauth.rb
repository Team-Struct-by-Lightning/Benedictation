OmniAuth.config.logger = Rails.logger

Rails.application.config.middleware.use OmniAuth::Builder do
  provider :google_oauth2, ENV['GOOGLE_KEY'], ENV['GOOGLE_SECRET'],
  {client_options: {ssl: {ca_file: Rails.root.join("cacert.pem").to_s}},
  access_type: 'offline', prompt: 'consent'}
end