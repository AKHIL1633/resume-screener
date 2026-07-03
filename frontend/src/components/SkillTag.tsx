interface SkillTagProps {
  skill: string
  variant?: 'default' | 'matched' | 'missing' | 'preferred'
}

const styles = {
  default: 'bg-slate-100 text-slate-700',
  matched: 'bg-green-100 text-green-700',
  missing: 'bg-red-100 text-red-600 line-through',
  preferred: 'bg-blue-100 text-blue-700',
}

export default function SkillTag({ skill, variant = 'default' }: SkillTagProps) {
  return (
    <span className={`inline-block px-2 py-0.5 rounded-full text-xs font-medium ${styles[variant]}`}>
      {skill}
    </span>
  )
}
