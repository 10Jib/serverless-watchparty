
# Serverless WatchParty


A simple project to allow users to host their own watchparty website on demand using AWS CDK and serverless components to start a Docker container as a task when the given DNS name sees activity.

Dosn't support permanent logins, or screen sharing.


TODO:
- [x] Add lambda function to start service and reroute dns requests
- [ ] Update Docker Script to output room usage to Cloud Watch.
- [ ] Add Cloud Watch Alarm to close service after unuse.
- [ ] Add env config file
- [ ] Experiemnt with other serverless services for faster coldstart, and lower costs.