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
    publishDate: z.preprocess((arg) => {
      if (typeof arg === 'string' || typeof arg === 'number') return new Date(arg);
      return arg;
    }, z.date()),
    pages: z.number().optional(),
    rating: z.number().optional(),
    tags: z.array(z.string()).optional(),
    featured: z.boolean().optional(),
    preview: z.object({
      type: z.enum(['words','break','percent']).default('words'),
      value: z.number().optional()
    }).optional()
  })
});

export const collections = { ebooks };
