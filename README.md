![Freelance Banner](https://s3.eu-central-1.amazonaws.com/static.expertcoder.io/github-banner/banner.png)

## Build PIP pakages for AWS Lambda

Any questions of issues, feel free to contact me, issue a pull request or raise an issue on this Git project.
Some of code this is specific to my own environment, small adjustments will be needed.

### How does this work?

A Cloudformation template creates a Lambda function and an S3 bucket. The pip packages are then built
on that actual Lambda function, and then sent to the S3 bucket. As added convenience a S3 pre-signed URL
is returned so the S3 object can downloaded.


### Why?

Some pip packages are specific to environments, so they need to be built/installed on a similar environment to
where they are used. This quickly allows you to build pip packages for lambda.

### TODO

* Update docs
* make `requirements.txt` easier to change.