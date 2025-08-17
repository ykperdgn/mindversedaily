import { defineCollection, z } from 'astro:content';

const ebooks = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    slug: z.string().optional(),
    author: z.string(),
    language: z.string().default('en'),
    amazonAsin: z.string(),
    amazonUrl: z.string().url(),
    cover: z.string().optional(),
    description: z.string().max(500).optional(),
    categories: z.array(z.string()).default([]),
    publishDate: z.date(),
    preview: z.object({
      type: z.enum(['words','break','percent']).default('words'),
      value: z.number().int().positive().optional()
    }).optional()
  })
});

export const collections = { ebooks };
