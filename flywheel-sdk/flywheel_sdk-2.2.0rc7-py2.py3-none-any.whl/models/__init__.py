# coding: utf-8

# flake8: noqa
"""
    Flywheel

    No description provided (generated by Swagger Codegen https://github.com/swagger-api/swagger-codegen)  # noqa: E501

    OpenAPI spec version: 2.2.0-rc.7
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


from __future__ import absolute_import

# import models into model package
from flywheel.models.acquisition import Acquisition
from flywheel.models.acquisition_metadata_input import AcquisitionMetadataInput
from flywheel.models.analysis_files_create_ticket_output import AnalysisFilesCreateTicketOutput
from flywheel.models.analysis_input import AnalysisInput
from flywheel.models.analysis_input_any import AnalysisInputAny
from flywheel.models.analysis_input_legacy import AnalysisInputLegacy
from flywheel.models.analysis_list_entry import AnalysisListEntry
from flywheel.models.analysis_output import AnalysisOutput
from flywheel.models.analysis_update import AnalysisUpdate
from flywheel.models.auth_login_output import AuthLoginOutput
from flywheel.models.auth_logout_output import AuthLogoutOutput
from flywheel.models.avatars import Avatars
from flywheel.models.batch import Batch
from flywheel.models.batch_cancel_output import BatchCancelOutput
from flywheel.models.batch_proposal import BatchProposal
from flywheel.models.batch_proposal_detail import BatchProposalDetail
from flywheel.models.batch_proposal_input import BatchProposalInput
from flywheel.models.classification_add_delete import ClassificationAddDelete
from flywheel.models.classification_replace import ClassificationReplace
from flywheel.models.classification_update_input import ClassificationUpdateInput
from flywheel.models.collection import Collection
from flywheel.models.collection_new_output import CollectionNewOutput
from flywheel.models.collection_node import CollectionNode
from flywheel.models.collection_operation import CollectionOperation
from flywheel.models.common_classification import CommonClassification
from flywheel.models.common_deleted_count import CommonDeletedCount
from flywheel.models.common_info import CommonInfo
from flywheel.models.common_modified_count import CommonModifiedCount
from flywheel.models.common_object_created import CommonObjectCreated
from flywheel.models.config_auth_output import ConfigAuthOutput
from flywheel.models.config_output import ConfigOutput
from flywheel.models.config_site_config_output import ConfigSiteConfigOutput
from flywheel.models.container_new_output import ContainerNewOutput
from flywheel.models.container_output_with_files import ContainerOutputWithFiles
from flywheel.models.container_reference import ContainerReference
from flywheel.models.device import Device
from flywheel.models.device_status import DeviceStatus
from flywheel.models.device_status_entry import DeviceStatusEntry
from flywheel.models.download import Download
from flywheel.models.download_filter import DownloadFilter
from flywheel.models.download_filter_definition import DownloadFilterDefinition
from flywheel.models.download_input import DownloadInput
from flywheel.models.download_node import DownloadNode
from flywheel.models.download_ticket import DownloadTicket
from flywheel.models.download_ticket_with_summary import DownloadTicketWithSummary
from flywheel.models.enginemetadata_engine_upload_input import EnginemetadataEngineUploadInput
from flywheel.models.enginemetadata_label_upload_input import EnginemetadataLabelUploadInput
from flywheel.models.enginemetadata_uid_match_upload_input import EnginemetadataUidMatchUploadInput
from flywheel.models.enginemetadata_uid_upload_input import EnginemetadataUidUploadInput
from flywheel.models.enginemetadata_upload_acquisition_metadata_input import EnginemetadataUploadAcquisitionMetadataInput
from flywheel.models.file_entry import FileEntry
from flywheel.models.file_origin import FileOrigin
from flywheel.models.file_reference import FileReference
from flywheel.models.file_via import FileVia
from flywheel.models.gear import Gear
from flywheel.models.gear_config import GearConfig
from flywheel.models.gear_context_lookup import GearContextLookup
from flywheel.models.gear_context_lookup_item import GearContextLookupItem
from flywheel.models.gear_custom import GearCustom
from flywheel.models.gear_directive import GearDirective
from flywheel.models.gear_doc import GearDoc
from flywheel.models.gear_environment import GearEnvironment
from flywheel.models.gear_exchange import GearExchange
from flywheel.models.gear_input_item import GearInputItem
from flywheel.models.gear_inputs import GearInputs
from flywheel.models.group import Group
from flywheel.models.group_metadata_input import GroupMetadataInput
from flywheel.models.group_new_output import GroupNewOutput
from flywheel.models.info_add_remove import InfoAddRemove
from flywheel.models.info_replace import InfoReplace
from flywheel.models.info_update_input import InfoUpdateInput
from flywheel.models.inline_response_200 import InlineResponse200
from flywheel.models.inline_response_200_1 import InlineResponse2001
from flywheel.models.inline_response_200_2 import InlineResponse2002
from flywheel.models.inline_response_200_3 import InlineResponse2003
from flywheel.models.job import Job
from flywheel.models.job_config import JobConfig
from flywheel.models.job_destination import JobDestination
from flywheel.models.job_inputs_item import JobInputsItem
from flywheel.models.job_inputs_object import JobInputsObject
from flywheel.models.job_log import JobLog
from flywheel.models.job_log_statement import JobLogStatement
from flywheel.models.job_origin import JobOrigin
from flywheel.models.job_produced_metadata import JobProducedMetadata
from flywheel.models.job_request import JobRequest
from flywheel.models.modality import Modality
from flywheel.models.note import Note
from flywheel.models.packfile import Packfile
from flywheel.models.packfile_acquisition_input import PackfileAcquisitionInput
from flywheel.models.packfile_packfile_input import PackfilePackfileInput
from flywheel.models.packfile_project_input import PackfileProjectInput
from flywheel.models.packfile_session_input import PackfileSessionInput
from flywheel.models.packfile_start import PackfileStart
from flywheel.models.permission import Permission
from flywheel.models.project import Project
from flywheel.models.project_metadata_input import ProjectMetadataInput
from flywheel.models.project_template import ProjectTemplate
from flywheel.models.project_template_requirement import ProjectTemplateRequirement
from flywheel.models.report_demographics_grid import ReportDemographicsGrid
from flywheel.models.report_ethnicity_grid import ReportEthnicityGrid
from flywheel.models.report_gender_count import ReportGenderCount
from flywheel.models.report_group_report import ReportGroupReport
from flywheel.models.report_project import ReportProject
from flywheel.models.report_site import ReportSite
from flywheel.models.resolver_input import ResolverInput
from flywheel.models.resolver_node import ResolverNode
from flywheel.models.resolver_output import ResolverOutput
from flywheel.models.rule import Rule
from flywheel.models.rule_any import RuleAny
from flywheel.models.search_acquisition_response import SearchAcquisitionResponse
from flywheel.models.search_analysis_response import SearchAnalysisResponse
from flywheel.models.search_collection_response import SearchCollectionResponse
from flywheel.models.search_file_response import SearchFileResponse
from flywheel.models.search_group_response import SearchGroupResponse
from flywheel.models.search_parent_response import SearchParentResponse
from flywheel.models.search_project_response import SearchProjectResponse
from flywheel.models.search_query import SearchQuery
from flywheel.models.search_response import SearchResponse
from flywheel.models.search_session_response import SearchSessionResponse
from flywheel.models.search_subject_response import SearchSubjectResponse
from flywheel.models.session import Session
from flywheel.models.session_jobs_output import SessionJobsOutput
from flywheel.models.session_metadata_input import SessionMetadataInput
from flywheel.models.session_template_recalc_output import SessionTemplateRecalcOutput
from flywheel.models.subject import Subject
from flywheel.models.tag import Tag
from flywheel.models.user import User
from flywheel.models.user_api_key import UserApiKey
from flywheel.models.user_preferences import UserPreferences
from flywheel.models.user_wechat import UserWechat
from flywheel.models.version_output import VersionOutput
from flywheel.models.resolver_acquisition_node import ResolverAcquisitionNode
from flywheel.models.resolver_file_node import ResolverFileNode
from flywheel.models.resolver_group_node import ResolverGroupNode
from flywheel.models.resolver_project_node import ResolverProjectNode
from flywheel.models.resolver_session_node import ResolverSessionNode
