import { CollectionConfig } from 'payload'

export const Projects: CollectionConfig = {
  slug: 'projects',
  access: {
    read: () => true,
    create: () => true,
    update: () => true,
    delete: () => true,
  },
  fields: [
    {
      name: 'title',
      type: 'text',
      required: true,
    },
    {
      name: 'floorplanData',
      type: 'json', // This stores our rooms, doors, fixtures, etc.
      required: true,
    },
    {
      name: 'status',
      type: 'select',
      options: [
        { label: 'Draft', value: 'draft' },
        { label: 'Compliant', value: 'compliant' },
        { label: 'Non-Compliant', value: 'non-compliant' },
      ],
      defaultValue: 'draft',
    },
  ],
}