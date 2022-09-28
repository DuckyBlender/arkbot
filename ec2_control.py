# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""
Purpose

Shows how to use AWS SDK for Python (Boto3) with the Amazon Elastic Compute Cloud
(Amazon EC2) API to manage aspects of an Amazon EC2 instance.
"""

import logging
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)
ec2 = boto3.resource('ec2')


def start_instance(instance_id):
    """
    Starts an instance. The request returns immediately. To wait for the instance
    to start, use the Instance.wait_until_running() function.

    :param instance_id: The ID of the instance to start.
    :return: The response to the start request. This includes both the previous and
             current state of the instance.
    """
    try:
        response = ec2.Instance(instance_id).start()
        logger.info("Started instance %s.", instance_id)
    except ClientError:
        logger.exception("Couldn't start instance %s.", instance_id)
        raise
    else:
        return response


def stop_instance(instance_id):
    """
    Stops an instance. The request returns immediately. To wait for the instance
    to stop, use the Instance.wait_until_stopped() function.

    :param instance_id: The ID of the instance to stop.
    :return: The response to the stop request. This includes both the previous and
             current state of the instance.
    """
    try:
        response = ec2.Instance(instance_id).stop()
        logger.info("Stopped instance %s.", instance_id)
    except ClientError:
        logger.exception("Couldn't stop instance %s.", instance_id)
        raise
    else:
        return response

def instance_status(instance_id):
    """
    Gets the status of the specified instance.

    :param instance_id: The ID of the instance.
    :return: The status of the instance.
    """
    try:
        status = ec2.Instance(instance_id).state['Name']
        logger.info("Got status for instance %s.", instance_id)
    except ClientError:
        logger.exception(("Couldn't get status for instance %s.", instance_id))
        raise
    else:
        return status

def get_console_output(instance_id):
    """
    Gets the console output of the specified instance.

    :param instance_id: The ID of the instance.
    :return: The console output as a string.
    """
    try:
        output = ec2.Instance(instance_id).console_output()['Output']
        logger.info("Got console output for instance %s.", instance_id)
    except ClientError:
        logger.exception(("Couldn't get console output for instance %s.", instance_id))
        raise
    else:
        return output

def get_elastic_ip(instance_id):
    """
    Gets the elastic IP address of the specified instance.

    :param instance_id: The ID of the instance.
    :return: The elastic IP address as a string.
    """
    try:
        ip = ec2.Instance(instance_id).public_ip_address
        logger.info("Got elastic IP for instance %s.", instance_id)
    except ClientError:
        logger.exception(("Couldn't get elastic IP for instance %s.", instance_id))
        raise
    else:
        return ip