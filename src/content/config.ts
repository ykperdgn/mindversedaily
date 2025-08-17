// Restored ebooks collection schema.
import { defineCollection, z } from 'astro:content';

const ebooks = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    author: z.string(),
    language: z.string().default('en'),
    amazonAsin: z.string(),
    amazonUrl: z.string().url(),
    cover: z.string().optional(),
    description: z.string(),
    categories: z.array(z.string()).default([]),
    publishDate: z.date(),
    preview: z.object({
      type: z.enum(['words','break','percent']).default('words'),
      value: z.number().optional()
    }).optional()
  })
});

export const collections = { ebooks };
