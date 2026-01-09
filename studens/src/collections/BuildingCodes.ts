import { CollectionConfig } from 'payload'

export const BuildingCodes: CollectionConfig = {
  slug: 'building-codes',
  admin: {
    useAsTitle: 'ruleName',
    defaultColumns: ['ruleName', 'codeProfile', 'thresholdValue', 'featureKey'],
  },
  fields: [
    {
      name: 'ruleName',
      type: 'text',
      required: true, 
      label: 'Rule Name' // e.g. "Min Door Width (Malaysia)"
    },
    {
      name: 'codeProfile',
      type: 'select',
      required: true,
      options: [
        { label: 'USA - International Building Code (IBC 2018)', value: 'IBC_2018' },
        { label: 'Malaysia - UBBL 1984 (Amd 2012)', value: 'UBBL_1984' },
        { label: 'Universal Design (Gold Standard)', value: 'Universal_Design' },
      ],
      defaultValue: 'IBC_2018',
    },
    {
      name: 'featureKey',
      type: 'select',
      required: true,
      options: [
        { label: 'Door Width (KR1)', value: 'door_width' },
        { label: 'Room Area (KR2)', value: 'room_area' },
        { label: 'Fixture Clearance (KR3)', value: 'fixture_clearance' },
        { label: 'Ceiling Height (KR4)', value: 'ceiling_height' },
        { label: 'Egress Path Width (KR5)', value: 'egress_width' },
      ],
    },
    {
      name: 'thresholdValue',
      type: 'number',
      required: true,
      admin: {
        description: 'Value in mm or m²',
      },
    },
    {
      name: 'operator',
      type: 'select',
      defaultValue: 'gte',
      options: [
        { label: '>= (Greater Than or Equal)', value: 'gte' },
        { label: '<= (Less Than or Equal)', value: 'lte' },
      ]
    }
  ],
}