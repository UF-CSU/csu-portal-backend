"""
Import/upload data tests.
"""

from django.contrib.postgres.aggregates import StringAgg
from django.db import models

from querycsv.models import QueryCsvUploadJob
from querycsv.services import QueryCsvService
from querycsv.tests.utils import (
    CsvDataM2MTestsBase,
    CsvDataM2OTestsBase,
    UploadCsvTestsBase,
)


class UploadCsvTests(UploadCsvTestsBase):
    """
    Test uploading data from a csv.

    Overrides
    ---------
    Required:
        - model_class
        - serializer_class
        - def get_create_params
        - def get_update_params

    Optional:
        - dataset_size
        - unique_field
    """

    def test_create_objects_from_csv(self):
        """Should be able to take csv and create models."""

        # Initialize data
        objects_before = self.initialize_csv_data()

        # Call service upload function
        _, failed = self.service.upload_csv(path=self.filepath)

        # Validate database
        self.assertObjectsExist(objects_before, failed)
        self.assertObjectsHaveFields(objects_before)

    def test_update_objects_from_csv(self):
        # Initialize data
        objects_before = self.initialize_csv_data(clear_db=False)

        for obj in self.repo.all():
            self.update_mock_object(obj)

        # Call service upload function
        self.service.upload_csv(path=self.filepath)

        # Validate database
        self.assertObjectsExist(objects_before)
        self.assertObjectsHaveFields(objects_before)

    def test_upload_csv_bad_fields(self):
        """Should create objects and ignore bad fields."""

        # Initialize csv, add invalid column
        objects_before = self.initialize_csv_data()
        self.df["Invalid field"] = "bad value"
        self.df_to_csv(self.df)

        self.assertTrue("Invalid field" in list(self.df.columns))

        self.service.upload_csv(path=self.filepath)

        # Validate database
        self.assertObjectsExist(objects_before)
        self.assertObjectsHaveFields(objects_before)

    def test_upload_csv_update_objects(self):
        """Uploading a csv should update objects."""

        # Prep data, create csv
        objects_before = self.initialize_csv_data(clear_db=False)

        updated_records = []

        for obj in objects_before:
            payload = {self.unique_field: obj[self.unique_field]}
            payload = self.get_update_params(obj, **payload)
            updated_records.append(payload)

        self.data_to_csv(updated_records)

        # Upload CSV
        self.service.upload_csv(path=self.filepath)

        # Validate data
        self.assertObjectsHaveFields(updated_records)

    def test_upload_csv_spaces(self):
        """Should remove pre/post spaces from fields before updating/creating."""

        # Prep data, create csv
        objects_before = self.initialize_csv_data(clear_db=False)

        updated_records = []

        for obj in objects_before:
            payload = {self.unique_field: f"  {obj[self.unique_field]}  "}
            payload = self.get_update_params(obj, **payload)
            updated_records.append(payload)

        self.data_to_csv(updated_records)
        self.assertObjectsExist(objects_before)

        # Upload CSV
        self.service.upload_csv(path=self.filepath)

        # Validate data
        self.assertObjectsHaveFields(updated_records)


class UploadCsvJobTests(UploadCsvTestsBase):
    """Tests for uploading with QSCsv Model."""

    def test_upload_from_job(self):
        """Should upload and process csv from model."""

        # Initialize data
        objects_before = self.initialize_csv_data(clear_db=False)

        # Update fields after create csv
        for obj in self.repo.all():
            self.update_mock_object(obj)

        # Upload csv via service
        job = QueryCsvUploadJob.objects.create(
            filepath=self.filepath,
            serializer_class=self.serializer_class,
        )
        QueryCsvService.upload_from_job(job)

        # Validate database
        self.assertObjectsExist(objects_before)
        self.assertObjectsHaveFields(objects_before)

    def test_upload_custom_fields(self):
        """Should process csv with custom field mappings."""

        objects_before = self.initialize_csv_data()

        # Rename csv field
        self.df.rename(columns={"name": "Test Value"}, inplace=True)
        self.df_to_csv(self.df, self.filepath)

        # Create and upload job
        job = QueryCsvUploadJob.objects.create(
            serializer_class=self.serializer_class, filepath=self.filepath
        )
        job.add_field_mapping(column_name="Test Value", field_name="name")
        job.refresh_from_db()

        QueryCsvService.upload_from_job(job)

        # Validate database
        self.assertObjectsExist(pre_queryset=objects_before)
        self.assertObjectsHaveFields(expected_objects=objects_before)


class UploadCsvM2OFieldsTests(UploadCsvTestsBase, CsvDataM2OTestsBase):
    """Test uploading csvs for models with many-to-one fields."""

    def test_upload_csv_m2o_fields(self):
        """
        Should present Many-to-One (FK) fields according to serializer.

        Check by comparing the serialized representation before and after
        the upload - both should have the save value for writable fields.
        """

        # Initialize data
        objects_before = self.initialize_csv_data()

        # Call upload function
        self.service.upload_csv(path=self.filepath)

        # Validate database
        self.assertObjectsHaveFields(objects_before)
        self.assertIn(self.m2o_selector, list(self.df.columns))

        self.assertObjectsM2OValidFields(self.df)

    def test_upload_csv_m2o_fields_update(self):
        """Should update models with Many-to-One fields."""

        # Initialize data
        objects_before = self.initialize_csv_data(clear_db=False)

        # Update fields after create csv
        for obj in self.repo.all():
            self.update_mock_object(obj)

        # Call upload function
        self.service.upload_csv(path=self.filepath)

        # Validate database
        self.assertObjectsHaveFields(objects_before)
        self.assertIn(self.m2o_selector, list(self.df.columns))

        self.assertObjectsM2OValidFields(self.df)


class UploadCsvM2MFieldsTests(UploadCsvTestsBase, CsvDataM2MTestsBase):
    """Test uploading csvs for models with many-to-many fields."""

    def test_upload_csv_m2m_fields(self):
        """When csv is uploaded, m2m fields should be handled properly."""

        # Initialize data
        objects_before = self.initialize_csv_data()

        # Upload csv using service
        self.service.upload_csv(path=self.filepath)

        # Validate results
        self.assertObjectsHaveFields(objects_before)
        self.assertIn(self.m2m_selector, list(self.df.columns))

        self.assertObjectsM2MValidFields(self.df)

    def test_upload_csv_m2m_fields_spaces(self):
        """When csv is uploaded, m2m fields should be stripped of leading/trailing spaces."""

        objects_before = self.initialize_csv_data()

        # Iterate through csv, manually add spacing
        for i, row in self.df.iterrows():
            pre_value = row[self.m2m_selector]
            pre_values = pre_value.split(",")
            modified_value = "  ,  ".join(pre_values)
            row[self.m2m_selector] = modified_value

        self.df_to_csv(self.df)

        # Upload csv using service
        self.service.upload_csv(path=self.filepath)

        # Validate results
        self.assertObjectsHaveFields(objects_before)
        self.assertIn(self.m2m_selector, list(self.df.columns))

        self.assertObjectsM2MValidFields(self.df)

    def test_upload_csv_m2m_update_fields(self):
        """When csv is uploaded, should update objects with many-to-many fields."""

        # Initialize data
        objects_before = self.initialize_csv_data(clear_db=False)

        # Update fields after create csv
        self.update_dataset()
        # for obj in self.repo.all().prefetch_related(self.m2m_selector):
        #     self.update_mock_object(obj)

        objects_before = list(
            self.repo.all()
            .annotate(
                pre_objs_count=models.Count(self.m2m_selector),
                pre_objs=StringAgg(
                    models.F(f"{self.m2m_selector}__{self.m2m_target_field}"),
                    distinct=True,
                    delimiter=",",
                ),
            )
            .values()
        )

        # Upload csv using service
        success, failed = self.service.upload_csv(path=self.filepath)

        # Validate results
        self.assertEqual(self.repo.all().count(), self.dataset_size)
        expected_objects = list(self.df.to_dict("records"))

        self.assertObjectsHaveFields(expected_objects)
        self.assertIn(self.m2m_selector, list(self.df.columns))
        self.assertTrue(
            self.m2m_repo.all().count() <= self.m2m_size + self.m2m_update_size,
            f"Expected at most {self.m2m_size + self.m2m_update_size} M2M objects, "
            f"but {self.m2m_repo.all().count()} were created.",
        )

        self.assertObjectsM2MValidFields(self.df, objects_before)
