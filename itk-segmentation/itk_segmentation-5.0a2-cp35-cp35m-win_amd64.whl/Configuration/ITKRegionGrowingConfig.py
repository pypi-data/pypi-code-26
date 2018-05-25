depends = ('ITKPyBase', 'ITKThresholding', )
templates = (
  ('ConfidenceConnectedImageFilter', 'itk::ConfidenceConnectedImageFilter', 'itkConfidenceConnectedImageFilterISS2ISS2', True, 'itk::Image< signed short,2 >, itk::Image< signed short,2 >'),
  ('ConfidenceConnectedImageFilter', 'itk::ConfidenceConnectedImageFilter', 'itkConfidenceConnectedImageFilterISS3ISS3', True, 'itk::Image< signed short,3 >, itk::Image< signed short,3 >'),
  ('ConfidenceConnectedImageFilter', 'itk::ConfidenceConnectedImageFilter', 'itkConfidenceConnectedImageFilterISS2IUC2', True, 'itk::Image< signed short,2 >, itk::Image< unsigned char,2 >'),
  ('ConfidenceConnectedImageFilter', 'itk::ConfidenceConnectedImageFilter', 'itkConfidenceConnectedImageFilterISS3IUC3', True, 'itk::Image< signed short,3 >, itk::Image< unsigned char,3 >'),
  ('ConfidenceConnectedImageFilter', 'itk::ConfidenceConnectedImageFilter', 'itkConfidenceConnectedImageFilterISS2IUS2', True, 'itk::Image< signed short,2 >, itk::Image< unsigned short,2 >'),
  ('ConfidenceConnectedImageFilter', 'itk::ConfidenceConnectedImageFilter', 'itkConfidenceConnectedImageFilterISS3IUS3', True, 'itk::Image< signed short,3 >, itk::Image< unsigned short,3 >'),
  ('ConfidenceConnectedImageFilter', 'itk::ConfidenceConnectedImageFilter', 'itkConfidenceConnectedImageFilterIUC2ISS2', True, 'itk::Image< unsigned char,2 >, itk::Image< signed short,2 >'),
  ('ConfidenceConnectedImageFilter', 'itk::ConfidenceConnectedImageFilter', 'itkConfidenceConnectedImageFilterIUC3ISS3', True, 'itk::Image< unsigned char,3 >, itk::Image< signed short,3 >'),
  ('ConfidenceConnectedImageFilter', 'itk::ConfidenceConnectedImageFilter', 'itkConfidenceConnectedImageFilterIUC2IUC2', True, 'itk::Image< unsigned char,2 >, itk::Image< unsigned char,2 >'),
  ('ConfidenceConnectedImageFilter', 'itk::ConfidenceConnectedImageFilter', 'itkConfidenceConnectedImageFilterIUC3IUC3', True, 'itk::Image< unsigned char,3 >, itk::Image< unsigned char,3 >'),
  ('ConfidenceConnectedImageFilter', 'itk::ConfidenceConnectedImageFilter', 'itkConfidenceConnectedImageFilterIUC2IUS2', True, 'itk::Image< unsigned char,2 >, itk::Image< unsigned short,2 >'),
  ('ConfidenceConnectedImageFilter', 'itk::ConfidenceConnectedImageFilter', 'itkConfidenceConnectedImageFilterIUC3IUS3', True, 'itk::Image< unsigned char,3 >, itk::Image< unsigned short,3 >'),
  ('ConfidenceConnectedImageFilter', 'itk::ConfidenceConnectedImageFilter', 'itkConfidenceConnectedImageFilterIUS2ISS2', True, 'itk::Image< unsigned short,2 >, itk::Image< signed short,2 >'),
  ('ConfidenceConnectedImageFilter', 'itk::ConfidenceConnectedImageFilter', 'itkConfidenceConnectedImageFilterIUS3ISS3', True, 'itk::Image< unsigned short,3 >, itk::Image< signed short,3 >'),
  ('ConfidenceConnectedImageFilter', 'itk::ConfidenceConnectedImageFilter', 'itkConfidenceConnectedImageFilterIUS2IUC2', True, 'itk::Image< unsigned short,2 >, itk::Image< unsigned char,2 >'),
  ('ConfidenceConnectedImageFilter', 'itk::ConfidenceConnectedImageFilter', 'itkConfidenceConnectedImageFilterIUS3IUC3', True, 'itk::Image< unsigned short,3 >, itk::Image< unsigned char,3 >'),
  ('ConfidenceConnectedImageFilter', 'itk::ConfidenceConnectedImageFilter', 'itkConfidenceConnectedImageFilterIUS2IUS2', True, 'itk::Image< unsigned short,2 >, itk::Image< unsigned short,2 >'),
  ('ConfidenceConnectedImageFilter', 'itk::ConfidenceConnectedImageFilter', 'itkConfidenceConnectedImageFilterIUS3IUS3', True, 'itk::Image< unsigned short,3 >, itk::Image< unsigned short,3 >'),
  ('ConfidenceConnectedImageFilter', 'itk::ConfidenceConnectedImageFilter', 'itkConfidenceConnectedImageFilterIF2ISS2', True, 'itk::Image< float,2 >, itk::Image< signed short,2 >'),
  ('ConfidenceConnectedImageFilter', 'itk::ConfidenceConnectedImageFilter', 'itkConfidenceConnectedImageFilterIF3ISS3', True, 'itk::Image< float,3 >, itk::Image< signed short,3 >'),
  ('ConfidenceConnectedImageFilter', 'itk::ConfidenceConnectedImageFilter', 'itkConfidenceConnectedImageFilterIF2IUC2', True, 'itk::Image< float,2 >, itk::Image< unsigned char,2 >'),
  ('ConfidenceConnectedImageFilter', 'itk::ConfidenceConnectedImageFilter', 'itkConfidenceConnectedImageFilterIF3IUC3', True, 'itk::Image< float,3 >, itk::Image< unsigned char,3 >'),
  ('ConfidenceConnectedImageFilter', 'itk::ConfidenceConnectedImageFilter', 'itkConfidenceConnectedImageFilterIF2IUS2', True, 'itk::Image< float,2 >, itk::Image< unsigned short,2 >'),
  ('ConfidenceConnectedImageFilter', 'itk::ConfidenceConnectedImageFilter', 'itkConfidenceConnectedImageFilterIF3IUS3', True, 'itk::Image< float,3 >, itk::Image< unsigned short,3 >'),
  ('ConnectedThresholdImageFilter', 'itk::ConnectedThresholdImageFilter', 'itkConnectedThresholdImageFilterISS2ISS2', True, 'itk::Image< signed short,2 >, itk::Image< signed short,2 >'),
  ('ConnectedThresholdImageFilter', 'itk::ConnectedThresholdImageFilter', 'itkConnectedThresholdImageFilterISS3ISS3', True, 'itk::Image< signed short,3 >, itk::Image< signed short,3 >'),
  ('ConnectedThresholdImageFilter', 'itk::ConnectedThresholdImageFilter', 'itkConnectedThresholdImageFilterIUC2IUC2', True, 'itk::Image< unsigned char,2 >, itk::Image< unsigned char,2 >'),
  ('ConnectedThresholdImageFilter', 'itk::ConnectedThresholdImageFilter', 'itkConnectedThresholdImageFilterIUC3IUC3', True, 'itk::Image< unsigned char,3 >, itk::Image< unsigned char,3 >'),
  ('ConnectedThresholdImageFilter', 'itk::ConnectedThresholdImageFilter', 'itkConnectedThresholdImageFilterIUS2IUS2', True, 'itk::Image< unsigned short,2 >, itk::Image< unsigned short,2 >'),
  ('ConnectedThresholdImageFilter', 'itk::ConnectedThresholdImageFilter', 'itkConnectedThresholdImageFilterIUS3IUS3', True, 'itk::Image< unsigned short,3 >, itk::Image< unsigned short,3 >'),
  ('ConnectedThresholdImageFilter', 'itk::ConnectedThresholdImageFilter', 'itkConnectedThresholdImageFilterIF2IF2', True, 'itk::Image< float,2 >, itk::Image< float,2 >'),
  ('ConnectedThresholdImageFilter', 'itk::ConnectedThresholdImageFilter', 'itkConnectedThresholdImageFilterIF3IF3', True, 'itk::Image< float,3 >, itk::Image< float,3 >'),
  ('IsolatedConnectedImageFilter', 'itk::IsolatedConnectedImageFilter', 'itkIsolatedConnectedImageFilterISS2ISS2', True, 'itk::Image< signed short,2 >, itk::Image< signed short,2 >'),
  ('IsolatedConnectedImageFilter', 'itk::IsolatedConnectedImageFilter', 'itkIsolatedConnectedImageFilterISS3ISS3', True, 'itk::Image< signed short,3 >, itk::Image< signed short,3 >'),
  ('IsolatedConnectedImageFilter', 'itk::IsolatedConnectedImageFilter', 'itkIsolatedConnectedImageFilterIUC2IUC2', True, 'itk::Image< unsigned char,2 >, itk::Image< unsigned char,2 >'),
  ('IsolatedConnectedImageFilter', 'itk::IsolatedConnectedImageFilter', 'itkIsolatedConnectedImageFilterIUC3IUC3', True, 'itk::Image< unsigned char,3 >, itk::Image< unsigned char,3 >'),
  ('IsolatedConnectedImageFilter', 'itk::IsolatedConnectedImageFilter', 'itkIsolatedConnectedImageFilterIUS2IUS2', True, 'itk::Image< unsigned short,2 >, itk::Image< unsigned short,2 >'),
  ('IsolatedConnectedImageFilter', 'itk::IsolatedConnectedImageFilter', 'itkIsolatedConnectedImageFilterIUS3IUS3', True, 'itk::Image< unsigned short,3 >, itk::Image< unsigned short,3 >'),
  ('IsolatedConnectedImageFilter', 'itk::IsolatedConnectedImageFilter', 'itkIsolatedConnectedImageFilterIF2IF2', True, 'itk::Image< float,2 >, itk::Image< float,2 >'),
  ('IsolatedConnectedImageFilter', 'itk::IsolatedConnectedImageFilter', 'itkIsolatedConnectedImageFilterIF3IF3', True, 'itk::Image< float,3 >, itk::Image< float,3 >'),
  ('NeighborhoodConnectedImageFilter', 'itk::NeighborhoodConnectedImageFilter', 'itkNeighborhoodConnectedImageFilterISS2ISS2', True, 'itk::Image< signed short,2 >, itk::Image< signed short,2 >'),
  ('NeighborhoodConnectedImageFilter', 'itk::NeighborhoodConnectedImageFilter', 'itkNeighborhoodConnectedImageFilterISS3ISS3', True, 'itk::Image< signed short,3 >, itk::Image< signed short,3 >'),
  ('NeighborhoodConnectedImageFilter', 'itk::NeighborhoodConnectedImageFilter', 'itkNeighborhoodConnectedImageFilterIUC2IUC2', True, 'itk::Image< unsigned char,2 >, itk::Image< unsigned char,2 >'),
  ('NeighborhoodConnectedImageFilter', 'itk::NeighborhoodConnectedImageFilter', 'itkNeighborhoodConnectedImageFilterIUC3IUC3', True, 'itk::Image< unsigned char,3 >, itk::Image< unsigned char,3 >'),
  ('NeighborhoodConnectedImageFilter', 'itk::NeighborhoodConnectedImageFilter', 'itkNeighborhoodConnectedImageFilterIUS2IUS2', True, 'itk::Image< unsigned short,2 >, itk::Image< unsigned short,2 >'),
  ('NeighborhoodConnectedImageFilter', 'itk::NeighborhoodConnectedImageFilter', 'itkNeighborhoodConnectedImageFilterIUS3IUS3', True, 'itk::Image< unsigned short,3 >, itk::Image< unsigned short,3 >'),
  ('NeighborhoodConnectedImageFilter', 'itk::NeighborhoodConnectedImageFilter', 'itkNeighborhoodConnectedImageFilterIF2IF2', True, 'itk::Image< float,2 >, itk::Image< float,2 >'),
  ('NeighborhoodConnectedImageFilter', 'itk::NeighborhoodConnectedImageFilter', 'itkNeighborhoodConnectedImageFilterIF3IF3', True, 'itk::Image< float,3 >, itk::Image< float,3 >'),
  ('VectorConfidenceConnectedImageFilter', 'itk::VectorConfidenceConnectedImageFilter', 'itkVectorConfidenceConnectedImageFilterIRGBUC2ISS2', True, 'itk::Image< itk::RGBPixel< unsigned char >,2 >, itk::Image< signed short,2 >'),
  ('VectorConfidenceConnectedImageFilter', 'itk::VectorConfidenceConnectedImageFilter', 'itkVectorConfidenceConnectedImageFilterIRGBUC3ISS3', True, 'itk::Image< itk::RGBPixel< unsigned char >,3 >, itk::Image< signed short,3 >'),
  ('VectorConfidenceConnectedImageFilter', 'itk::VectorConfidenceConnectedImageFilter', 'itkVectorConfidenceConnectedImageFilterIRGBUC2IUC2', True, 'itk::Image< itk::RGBPixel< unsigned char >,2 >, itk::Image< unsigned char,2 >'),
  ('VectorConfidenceConnectedImageFilter', 'itk::VectorConfidenceConnectedImageFilter', 'itkVectorConfidenceConnectedImageFilterIRGBUC3IUC3', True, 'itk::Image< itk::RGBPixel< unsigned char >,3 >, itk::Image< unsigned char,3 >'),
  ('VectorConfidenceConnectedImageFilter', 'itk::VectorConfidenceConnectedImageFilter', 'itkVectorConfidenceConnectedImageFilterIRGBUC2IUS2', True, 'itk::Image< itk::RGBPixel< unsigned char >,2 >, itk::Image< unsigned short,2 >'),
  ('VectorConfidenceConnectedImageFilter', 'itk::VectorConfidenceConnectedImageFilter', 'itkVectorConfidenceConnectedImageFilterIRGBUC3IUS3', True, 'itk::Image< itk::RGBPixel< unsigned char >,3 >, itk::Image< unsigned short,3 >'),
  ('VectorConfidenceConnectedImageFilter', 'itk::VectorConfidenceConnectedImageFilter', 'itkVectorConfidenceConnectedImageFilterIRGBAUC2ISS2', True, 'itk::Image< itk::RGBAPixel< unsigned char >,2 >, itk::Image< signed short,2 >'),
  ('VectorConfidenceConnectedImageFilter', 'itk::VectorConfidenceConnectedImageFilter', 'itkVectorConfidenceConnectedImageFilterIRGBAUC3ISS3', True, 'itk::Image< itk::RGBAPixel< unsigned char >,3 >, itk::Image< signed short,3 >'),
  ('VectorConfidenceConnectedImageFilter', 'itk::VectorConfidenceConnectedImageFilter', 'itkVectorConfidenceConnectedImageFilterIRGBAUC2IUC2', True, 'itk::Image< itk::RGBAPixel< unsigned char >,2 >, itk::Image< unsigned char,2 >'),
  ('VectorConfidenceConnectedImageFilter', 'itk::VectorConfidenceConnectedImageFilter', 'itkVectorConfidenceConnectedImageFilterIRGBAUC3IUC3', True, 'itk::Image< itk::RGBAPixel< unsigned char >,3 >, itk::Image< unsigned char,3 >'),
  ('VectorConfidenceConnectedImageFilter', 'itk::VectorConfidenceConnectedImageFilter', 'itkVectorConfidenceConnectedImageFilterIRGBAUC2IUS2', True, 'itk::Image< itk::RGBAPixel< unsigned char >,2 >, itk::Image< unsigned short,2 >'),
  ('VectorConfidenceConnectedImageFilter', 'itk::VectorConfidenceConnectedImageFilter', 'itkVectorConfidenceConnectedImageFilterIRGBAUC3IUS3', True, 'itk::Image< itk::RGBAPixel< unsigned char >,3 >, itk::Image< unsigned short,3 >'),
  ('VectorConfidenceConnectedImageFilter', 'itk::VectorConfidenceConnectedImageFilter', 'itkVectorConfidenceConnectedImageFilterIVF22ISS2', True, 'itk::Image< itk::Vector< float,2 >,2 >, itk::Image< signed short,2 >'),
  ('VectorConfidenceConnectedImageFilter', 'itk::VectorConfidenceConnectedImageFilter', 'itkVectorConfidenceConnectedImageFilterIVF23ISS3', True, 'itk::Image< itk::Vector< float,2 >,3 >, itk::Image< signed short,3 >'),
  ('VectorConfidenceConnectedImageFilter', 'itk::VectorConfidenceConnectedImageFilter', 'itkVectorConfidenceConnectedImageFilterIVF32ISS2', True, 'itk::Image< itk::Vector< float,3 >,2 >, itk::Image< signed short,2 >'),
  ('VectorConfidenceConnectedImageFilter', 'itk::VectorConfidenceConnectedImageFilter', 'itkVectorConfidenceConnectedImageFilterIVF33ISS3', True, 'itk::Image< itk::Vector< float,3 >,3 >, itk::Image< signed short,3 >'),
  ('VectorConfidenceConnectedImageFilter', 'itk::VectorConfidenceConnectedImageFilter', 'itkVectorConfidenceConnectedImageFilterIVF42ISS2', True, 'itk::Image< itk::Vector< float,4 >,2 >, itk::Image< signed short,2 >'),
  ('VectorConfidenceConnectedImageFilter', 'itk::VectorConfidenceConnectedImageFilter', 'itkVectorConfidenceConnectedImageFilterIVF43ISS3', True, 'itk::Image< itk::Vector< float,4 >,3 >, itk::Image< signed short,3 >'),
  ('VectorConfidenceConnectedImageFilter', 'itk::VectorConfidenceConnectedImageFilter', 'itkVectorConfidenceConnectedImageFilterIVF22IUC2', True, 'itk::Image< itk::Vector< float,2 >,2 >, itk::Image< unsigned char,2 >'),
  ('VectorConfidenceConnectedImageFilter', 'itk::VectorConfidenceConnectedImageFilter', 'itkVectorConfidenceConnectedImageFilterIVF23IUC3', True, 'itk::Image< itk::Vector< float,2 >,3 >, itk::Image< unsigned char,3 >'),
  ('VectorConfidenceConnectedImageFilter', 'itk::VectorConfidenceConnectedImageFilter', 'itkVectorConfidenceConnectedImageFilterIVF32IUC2', True, 'itk::Image< itk::Vector< float,3 >,2 >, itk::Image< unsigned char,2 >'),
  ('VectorConfidenceConnectedImageFilter', 'itk::VectorConfidenceConnectedImageFilter', 'itkVectorConfidenceConnectedImageFilterIVF33IUC3', True, 'itk::Image< itk::Vector< float,3 >,3 >, itk::Image< unsigned char,3 >'),
  ('VectorConfidenceConnectedImageFilter', 'itk::VectorConfidenceConnectedImageFilter', 'itkVectorConfidenceConnectedImageFilterIVF42IUC2', True, 'itk::Image< itk::Vector< float,4 >,2 >, itk::Image< unsigned char,2 >'),
  ('VectorConfidenceConnectedImageFilter', 'itk::VectorConfidenceConnectedImageFilter', 'itkVectorConfidenceConnectedImageFilterIVF43IUC3', True, 'itk::Image< itk::Vector< float,4 >,3 >, itk::Image< unsigned char,3 >'),
  ('VectorConfidenceConnectedImageFilter', 'itk::VectorConfidenceConnectedImageFilter', 'itkVectorConfidenceConnectedImageFilterIVF22IUS2', True, 'itk::Image< itk::Vector< float,2 >,2 >, itk::Image< unsigned short,2 >'),
  ('VectorConfidenceConnectedImageFilter', 'itk::VectorConfidenceConnectedImageFilter', 'itkVectorConfidenceConnectedImageFilterIVF23IUS3', True, 'itk::Image< itk::Vector< float,2 >,3 >, itk::Image< unsigned short,3 >'),
  ('VectorConfidenceConnectedImageFilter', 'itk::VectorConfidenceConnectedImageFilter', 'itkVectorConfidenceConnectedImageFilterIVF32IUS2', True, 'itk::Image< itk::Vector< float,3 >,2 >, itk::Image< unsigned short,2 >'),
  ('VectorConfidenceConnectedImageFilter', 'itk::VectorConfidenceConnectedImageFilter', 'itkVectorConfidenceConnectedImageFilterIVF33IUS3', True, 'itk::Image< itk::Vector< float,3 >,3 >, itk::Image< unsigned short,3 >'),
  ('VectorConfidenceConnectedImageFilter', 'itk::VectorConfidenceConnectedImageFilter', 'itkVectorConfidenceConnectedImageFilterIVF42IUS2', True, 'itk::Image< itk::Vector< float,4 >,2 >, itk::Image< unsigned short,2 >'),
  ('VectorConfidenceConnectedImageFilter', 'itk::VectorConfidenceConnectedImageFilter', 'itkVectorConfidenceConnectedImageFilterIVF43IUS3', True, 'itk::Image< itk::Vector< float,4 >,3 >, itk::Image< unsigned short,3 >'),
  ('VectorConfidenceConnectedImageFilter', 'itk::VectorConfidenceConnectedImageFilter', 'itkVectorConfidenceConnectedImageFilterICVF22ISS2', True, 'itk::Image< itk::CovariantVector< float,2 >,2 >, itk::Image< signed short,2 >'),
  ('VectorConfidenceConnectedImageFilter', 'itk::VectorConfidenceConnectedImageFilter', 'itkVectorConfidenceConnectedImageFilterICVF23ISS3', True, 'itk::Image< itk::CovariantVector< float,2 >,3 >, itk::Image< signed short,3 >'),
  ('VectorConfidenceConnectedImageFilter', 'itk::VectorConfidenceConnectedImageFilter', 'itkVectorConfidenceConnectedImageFilterICVF32ISS2', True, 'itk::Image< itk::CovariantVector< float,3 >,2 >, itk::Image< signed short,2 >'),
  ('VectorConfidenceConnectedImageFilter', 'itk::VectorConfidenceConnectedImageFilter', 'itkVectorConfidenceConnectedImageFilterICVF33ISS3', True, 'itk::Image< itk::CovariantVector< float,3 >,3 >, itk::Image< signed short,3 >'),
  ('VectorConfidenceConnectedImageFilter', 'itk::VectorConfidenceConnectedImageFilter', 'itkVectorConfidenceConnectedImageFilterICVF42ISS2', True, 'itk::Image< itk::CovariantVector< float,4 >,2 >, itk::Image< signed short,2 >'),
  ('VectorConfidenceConnectedImageFilter', 'itk::VectorConfidenceConnectedImageFilter', 'itkVectorConfidenceConnectedImageFilterICVF43ISS3', True, 'itk::Image< itk::CovariantVector< float,4 >,3 >, itk::Image< signed short,3 >'),
  ('VectorConfidenceConnectedImageFilter', 'itk::VectorConfidenceConnectedImageFilter', 'itkVectorConfidenceConnectedImageFilterICVF22IUC2', True, 'itk::Image< itk::CovariantVector< float,2 >,2 >, itk::Image< unsigned char,2 >'),
  ('VectorConfidenceConnectedImageFilter', 'itk::VectorConfidenceConnectedImageFilter', 'itkVectorConfidenceConnectedImageFilterICVF23IUC3', True, 'itk::Image< itk::CovariantVector< float,2 >,3 >, itk::Image< unsigned char,3 >'),
  ('VectorConfidenceConnectedImageFilter', 'itk::VectorConfidenceConnectedImageFilter', 'itkVectorConfidenceConnectedImageFilterICVF32IUC2', True, 'itk::Image< itk::CovariantVector< float,3 >,2 >, itk::Image< unsigned char,2 >'),
  ('VectorConfidenceConnectedImageFilter', 'itk::VectorConfidenceConnectedImageFilter', 'itkVectorConfidenceConnectedImageFilterICVF33IUC3', True, 'itk::Image< itk::CovariantVector< float,3 >,3 >, itk::Image< unsigned char,3 >'),
  ('VectorConfidenceConnectedImageFilter', 'itk::VectorConfidenceConnectedImageFilter', 'itkVectorConfidenceConnectedImageFilterICVF42IUC2', True, 'itk::Image< itk::CovariantVector< float,4 >,2 >, itk::Image< unsigned char,2 >'),
  ('VectorConfidenceConnectedImageFilter', 'itk::VectorConfidenceConnectedImageFilter', 'itkVectorConfidenceConnectedImageFilterICVF43IUC3', True, 'itk::Image< itk::CovariantVector< float,4 >,3 >, itk::Image< unsigned char,3 >'),
  ('VectorConfidenceConnectedImageFilter', 'itk::VectorConfidenceConnectedImageFilter', 'itkVectorConfidenceConnectedImageFilterICVF22IUS2', True, 'itk::Image< itk::CovariantVector< float,2 >,2 >, itk::Image< unsigned short,2 >'),
  ('VectorConfidenceConnectedImageFilter', 'itk::VectorConfidenceConnectedImageFilter', 'itkVectorConfidenceConnectedImageFilterICVF23IUS3', True, 'itk::Image< itk::CovariantVector< float,2 >,3 >, itk::Image< unsigned short,3 >'),
  ('VectorConfidenceConnectedImageFilter', 'itk::VectorConfidenceConnectedImageFilter', 'itkVectorConfidenceConnectedImageFilterICVF32IUS2', True, 'itk::Image< itk::CovariantVector< float,3 >,2 >, itk::Image< unsigned short,2 >'),
  ('VectorConfidenceConnectedImageFilter', 'itk::VectorConfidenceConnectedImageFilter', 'itkVectorConfidenceConnectedImageFilterICVF33IUS3', True, 'itk::Image< itk::CovariantVector< float,3 >,3 >, itk::Image< unsigned short,3 >'),
  ('VectorConfidenceConnectedImageFilter', 'itk::VectorConfidenceConnectedImageFilter', 'itkVectorConfidenceConnectedImageFilterICVF42IUS2', True, 'itk::Image< itk::CovariantVector< float,4 >,2 >, itk::Image< unsigned short,2 >'),
  ('VectorConfidenceConnectedImageFilter', 'itk::VectorConfidenceConnectedImageFilter', 'itkVectorConfidenceConnectedImageFilterICVF43IUS3', True, 'itk::Image< itk::CovariantVector< float,4 >,3 >, itk::Image< unsigned short,3 >'),
)
