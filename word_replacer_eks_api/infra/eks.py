
from typing import cast
from constructs import Construct  
import requests
from aws_cdk import (
    Duration,
    Stack,
    RemovalPolicy,      
    aws_iam as iam,
    aws_ec2 as ec2,
    aws_s3 as s3,   
    aws_eks as eks
)
 
#aws_region = os.environ['AWS_REGION'] 

class EKSStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, vpc: ec2.Vpc , **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
  
        self.vpc = vpc
        self.cluster_name='Primary_Cluster'
        self.cluster_env_name='Dev'
        self.eks_cluster = self._create_eks()
        self._create_nodes() 
        self._deploy_aws_load_balancer_controller()

    def _create_eks(self) -> eks.Cluster:
        self.cluster_admin_role = iam.Role(self, "ClusterAdminRole",
                                           assumed_by=cast(
                                               iam.IPrincipal,
                                               iam.CompositePrincipal(
                                                   iam.AccountRootPrincipal(),
                                                   iam.ServicePrincipal(
                                                       "ec2.amazonaws.com")
                                               )
                                           )
                                           )

        cluster_admin_policy_statement = {
            "Effect": "Allow",
            "Action": [
                "eks:DescribeCluster"
            ],
            "Resource": "arn:aws:eks:{region}:{account}:cluster/{cluster_name}-{cluster_env_name}".format(
                region=self.region,
                account=self.account,
                cluster_name=self.cluster_name,
                cluster_env_name=self.cluster_env_name,
            )
        }
        self.cluster_admin_role.add_to_policy(
            iam.PolicyStatement.from_json(cluster_admin_policy_statement))

        # Create SecurityGroup for the Control Plane ENIs
        eks_security_group = ec2.SecurityGroup(
            self,
            "EKSSecurityGroup",
            vpc=cast(ec2.IVpc, self.vpc),
            allow_all_outbound=True,
        )

        eks_security_group.add_ingress_rule(
            ec2.Peer.ipv4(self.vpc.vpc_cidr_block), ec2.Port.all_traffic()
        )
        # Create an EKS Cluster
        eks_cluster = eks.Cluster(
            self,
            "cluster",
            cluster_name=self.cluster_name +
            "-" + self.cluster_env_name,
            vpc=cast(ec2.IVpc, self.vpc),             
            vpc_subnets=[ec2.SubnetSelection(
                subnet_group_name="eks-control-plane")],
            masters_role=cast(iam.IRole, self.cluster_admin_role),
            default_capacity=0,
            security_group=cast(ec2.ISecurityGroup, eks_security_group),
            endpoint_access=eks.EndpointAccess.PRIVATE,
            version=eks.KubernetesVersion.V1_21,
        )

        return eks_cluster

    def _create_nodes(self) -> None:

        required_nodegroup_managed_policy = [
            iam.ManagedPolicy.from_aws_managed_policy_name(
                managed_policy_name="AmazonSSMManagedInstanceCore"),
            iam.ManagedPolicy.from_aws_managed_policy_name(
                managed_policy_name="AmazonEKSWorkerNodePolicy"),
            iam.ManagedPolicy.from_aws_managed_policy_name(
                managed_policy_name="AmazonEKS_CNI_Policy"),
            iam.ManagedPolicy.from_aws_managed_policy_name(
                managed_policy_name="AmazonEC2ContainerRegistryReadOnly"),
        ]
        # Create IAM Role For node groups
        ng_role = iam.Role(self, "DefaultNGRole",
                                      assumed_by=cast(
                                          iam.IPrincipal,
                                          iam.CompositePrincipal(
                                              iam.AccountRootPrincipal(),
                                              iam.ServicePrincipal(
                                                  "ec2.amazonaws.com")
                                          )
                                      ),
                                      managed_policies=required_nodegroup_managed_policy,
                                      )

        # On Demand subnets nodegroup
        self.eks_cluster.add_nodegroup_capacity(
            "DefaultNodegroup",
            nodegroup_name="default-ng",
            capacity_type=eks.CapacityType.ON_DEMAND,
            min_size=0,
            desired_size=2,
            max_size=10,
            ami_type=eks.NodegroupAmiType.AL2_X86_64,
            instance_types=[
                ec2.InstanceType("m5.large"),
            ],
            node_role=ng_role,
            subnets=ec2.SubnetSelection(subnet_group_name="Private")
        )

      
    def _deploy_aws_load_balancer_controller(self):
        aws_lb_controller_name = "aws-load-balancer-controller"

        aws_lb_controller_service_account = self.eks_cluster.add_service_account(
            "aws-load-balancer-controller",
            name=aws_lb_controller_name,
            namespace="kube-system"
        )
        resp = requests.get(
            "https://raw.githubusercontent.com/kubernetes-sigs/aws-load-balancer-controller/v2.2.0/docs/install/"
            "iam_policy.json"
        )
        aws_load_balancer_controller_policy = resp.json()

        for stmt in aws_load_balancer_controller_policy["Statement"]:
            aws_lb_controller_service_account.add_to_principal_policy(
                iam.PolicyStatement.from_json(stmt)) 

        aws_lb_controller_chart = self.eks_cluster.add_helm_chart(
            "aws-load-balancer-controller",
            chart="aws-load-balancer-controller",
            version="1.2.3",
            release="aws-lb-controller",
            repository="https://aws.github.io/eks-charts",
            namespace="kube-system",
            values={
                "clusterName": self.eks_cluster.cluster_name,
                "region": self.region,
                "vpcId": self.vpc.vpc_id,
                "serviceAccount": {
                    "create": False,
                    "name": aws_lb_controller_name
                },
                "replicaCount": 2
            }
        )
        aws_lb_controller_chart.node.add_dependency(
            aws_lb_controller_service_account)