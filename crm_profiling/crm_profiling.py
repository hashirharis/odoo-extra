from osv import fields,osv
from osv import orm


def _get_answers(cr, uid, ids):
	query = """
	select distinct(answer)
	from profile_question_yes_rel
	where profile in (%s)"""% ','.join([str(i) for i in ids ])

	cr.execute(query)
	ans_yes = [x[0] for x in cr.fetchall()]

	query = """
	select distinct(answer)
	from profile_question_no_rel
	where profile in (%s)"""% ','.join([str(i) for i in ids ])

	cr.execute(query)
	ans_no = [x[0] for x in cr.fetchall()]

	return [ans_yes, ans_no]


def _get_parents(cr, uid, ids):
	ids_to_check = ids
	cr.execute("""
	 select distinct(parent_id)
	 from crm_segmentation
	 where parent_id is not null
	 and id in (%s)""" % ','.join([str(i) for i in ids ]))

	parent_ids = [x[0] for x in cr.fetchall()]

	trigger = False
	for x in parent_ids:
		if x not in ids_to_check:
			ids_to_check.append(x)
			trigger = True

	if trigger:
		ids_to_check = _get_parents(cr, uid, ids_to_check)

	return ids_to_check


def test_prof(cr, uid, seg_id, pid, answers_ids = []):
#return True if the partner pid fetch the segmentation rule seg_id
	ids_to_check = _get_parents(cr, uid, [seg_id])
	[yes_answers, no_answers] = _get_answers(cr, uid, ids_to_check)
	temp = True
	for y_ans in yes_answers:
		if y_ans not in answers_ids:
			temp = False
			break
	if temp:
		for ans in answers_ids:
			if ans in no_answers:
				temp = False
				break
	if temp:
		return True
	return False


def _recompute_categ(self, cr, uid, pid, answers_ids):
	ok =  []
	cr.execute('''
		select r.category_id 
		from res_partner_category_rel r left join crm_segmentation s on (r.category_id = s.categ_id) 
		where r.partner_id = %d and (s.exclusif = false or s.exclusif is null);
		'''% pid)
	for x in cr.fetchall():
		ok.append(x[0])

	query = '''
		select id, categ_id 
		from crm_segmentation 
		where profiling_active = true''' 
	if ok != []:
		query = query +''' and categ_id not in(%s)'''% ','.join([str(i) for i in ok ])
	query = query + ''' order by id '''

	cr.execute(query)
	segm_cat_ids = cr.fetchall()

	for (segm_id, cat_id) in segm_cat_ids:
		if test_prof(cr, uid, segm_id, pid, answers_ids):
			ok.append(cat_id)
	return ok


class question(osv.osv):
	_name="crm_profiling.question"
	_description= "Question"
	_columns={
		'name': fields.char("Question",size=128, required=True),
		'answers_ids': fields.one2many("crm_profiling.answer","question_id","Avalaible answers",),
		}

question()


class questionnaire(osv.osv):
	_name="crm_profiling.questionnaire"
	_description= "Questionnaire"
	_columns={
		'name': fields.char("Questionnaire",size=128, required=True),
		'description':fields.text("Description", required=True),
		'questions_ids': fields.many2many('crm_profiling.question','profile_questionnaire_quest_rel','questionnaire', 'question', "Questions"),
		}

questionnaire()


class answer(osv.osv):
	_name="crm_profiling.answer"
	_description="Answer"
	_columns={
		"name": fields.char("Answer",size=128, required=True),
		"question_id": fields.many2one('crm_profiling.question',"Question"),
		}
answer()


class partner(osv.osv):
	_inherit="res.partner"
	_columns={
		"answers_ids": fields.many2many("crm_profiling.answer","partner_question_rel","partner","answer","Answers"),
		}

	def write(self, cr, uid, ids, vals, context=None):
		if not context:
			context={}
		if 'answers_ids' in vals:
			vals['category_id']=[[6, 0, _recompute_categ(self, cr, uid, ids[0], vals['answers_ids'][0][2])]]
		return super(partner, self).write(cr, uid, ids, vals, context=context)

partner()


class crm_segmentation(osv.osv):
	_inherit="crm.segmentation"
	_columns={
		"answer_yes": fields.many2many("crm_profiling.answer","profile_question_yes_rel","profile","answer","Inclued answers"),
		"answer_no": fields.many2many("crm_profiling.answer","profile_question_no_rel","profile","answer","Excluded answers"),
		'parent_id': fields.many2one('crm.segmentation', 'Parent Profile'),
		'child_ids': fields.one2many('crm.segmentation', 'parent_id', 'Childs profile'),
		'profiling_active': fields.boolean('Use The Profiling Rules', help='Check if you want to use this tab as part of the segmentation rule. If not checked, the criteria beneath will be ignored')
		}
	_constraints = [
		(orm.orm.check_recursion, 'Error ! You can not create recursive profiles.', ['parent_id'])
	]

	def process_continue(self, cr, uid, ids, start=False):
		categs = self.read(cr,uid,ids,['categ_id','exclusif','partner_id', 'sales_purchase_active', 'profiling_active'])
		for categ in categs:
			if start:
				if categ['exclusif']:
					cr.execute('delete from res_partner_category_rel where category_id=%d', (categ['categ_id'][0],))

			id = categ['id']			

			cr.execute('select id from res_partner order by id ')
			partners = [x[0] for x in cr.fetchall()]

			if categ['sales_purchase_active']:
				to_remove_list=[]
				cr.execute('select id from crm_segmentation_line where segmentation_id=%d', (id,))
				line_ids = [x[0] for x in cr.fetchall()]

				for pid in partners:
					if (not self.pool.get('crm.segmentation.line').test(cr, uid, line_ids, pid)):
						to_remove_list.append(pid)
				for pid in to_remove_list:
					partners.remove(pid)

			if categ['profiling_active']:
				to_remove_list=[]
				for pid in partners:

					cr.execute('select distinct(answer) from partner_question_rel where partner=%d' % pid)
					answers_ids = [x[0] for x in cr.fetchall()]

					if (not test_prof(cr, uid, id, pid, answers_ids)):
						to_remove_list.append(pid)
				for pid in to_remove_list:
					partners.remove(pid)

			for partner_id in partners:
				cr.execute('insert into res_partner_category_rel (category_id,partner_id) values (%d,%d)', (categ['categ_id'][0],partner_id))
			cr.commit()

			self.write(cr, uid, [id], {'state':'not running', 'partner_id':0})
			cr.commit()
		return True

crm_segmentation()
