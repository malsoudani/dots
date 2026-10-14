export interface TeamMember {
  readonly id: string;
  readonly email: string;
  readonly name: string;
}

export interface TeamMemberResponse {
  readonly id: string;
  readonly email: string;
  readonly name?: string | null;
}

export const TeamMember = {
  fromResponse(raw: TeamMemberResponse): TeamMember {
    return { id: raw.id, email: raw.email, name: raw.name ?? "" };
  },
};
