OmniAuth.config.logger = Rails.logger

Rails.application.config.middleware.use OmniAuth::Builder do
  provider :google_oauth2,
  '165043768486-h54df8d1s3id58p9c603q3cq90pe60it.apps.googleusercontent.com',
  'fuXwRcqNZAu7iBIqwzAliLx_', {client_options: {ssl: {ca_file: Rails.root.join("cacert.pem").to_s}},
  access_type: 'offline'}
end