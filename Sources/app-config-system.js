/**
 * SPDX-FileCopyrightText: 2023 Sebastien Jodogne, UCLouvain, Belgium,
 * and 2018-2023 Open Health Imaging Foundation
 * SPDX-License-Identifier: MIT
 */

window.config.routerBasename = '${ROUTER_BASENAME}';

if (${USE_DICOM_WEB}) {
  window.config.dataSources = [
    {
      friendlyName: 'Orthanc DICOMweb',
      namespace: '@ohif/extension-default.dataSourcesModule.dicomweb',
      sourceName: 'dicomweb',
      configuration: {
        name: 'orthanc',

        wadoUriRoot: '../dicom-web',
        qidoRoot: '../dicom-web',
        wadoRoot: '../dicom-web',
        
        qidoSupportsIncludeField: false,
        supportsReject: false,
        imageRendering: 'wadors',
        thumbnailRendering: 'wadors',
        enableStudyLazyLoad: true,
        supportsFuzzyMatching: false,
        supportsWildcard: true,
        staticWado: true,
        singlepart: 'bulkdata'
      }
    }
  ];

  window.config.defaultDataSourceName = 'dicomweb';

} else {
  window.config.showStudyList = false;
  window.config.dataSources = [
    {
      friendlyName: 'Orthanc DICOM JSON',
      namespace: '@ohif/extension-default.dataSourcesModule.dicomjson',
      sourceName: 'dicomjson',
      configuration: {
        name: 'json',
      },
    }
  ];

  window.config.defaultDataSourceName = 'dicomjson';
}
